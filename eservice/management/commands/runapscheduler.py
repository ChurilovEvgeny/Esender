import logging
from smtplib import SMTPAuthenticationError, SMTPException

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from config.settings import EMAIL_HOST_USER
from eservice.models import Newsletter, AttemptsNewsletter

logger = logging.getLogger(__name__)

import threading


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.operation_completed = False
        self.operation_text = ""
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.html_content,
                EMAIL_HOST_USER,
                self.recipient_list,
                fail_silently=False,
            )
            self.operation_completed = True
        except SMTPAuthenticationError:
            self.operation_text = "Не удалось авторизоваться на почте"
        except SMTPException as e:
            self.operation_text = "SMTPException " + str(e)
        except Exception as e:
            self.operation_text = "Exception " + str(e)


def send_mail_async(subject, html_content, recipient_list):
    EmailThread(subject, html_content, recipient_list).start()


def send(newsletter: Newsletter):
    send_time = timezone.now()

    clients = newsletter.clients.get_queryset()

    email_threads = []
    for client in clients:
        email_threads.append(EmailThread(newsletter.message.subject, newsletter.message.body, [client.email]))

    print("Send started")
    [email_thread.start() for email_thread in email_threads]
    [email_thread.join() for email_thread in email_threads]
    print("Send competed")

    res = make_operation_result(email_threads)
    print(res)
    return send_time, res[0], res[1]
    # send_mail_async(newsletter.message.subject, newsletter.message.body, [client.email])


def make_operation_result(email_threads: list[EmailThread]) -> tuple[bool, str]:
    # По тз сказано, что у одной попытки рассылки должна быть одна запись в БД, без привязки к количеству клиентов
    # Поэтому сделан такой алгоритм

    # Если все в ошибках, то берем сообщение первого
    is_all_in_error = all([not email_thread.operation_completed for email_thread in email_threads])
    if is_all_in_error:
        return False, email_threads[0].operation_text
    # Если хотя-бы один без ошибки, то записываем успешную отправку
    else:
        return True, "OK"


def job_every_minute():
    print("EVERY minute")

    newsletters = Newsletter.get_newsletters_ready_to_sent()
    for newsletter in newsletters:
        operation_result = send(newsletter)

        newsletter.set_next_sent_datetime()
        newsletter.refresh_status()
        AttemptsNewsletter.objects.create(newsletter=newsletter, date_time_last_sent=operation_result[0],
                                          status=operation_result[1], mail_server_response=operation_result[2])


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Планировщик, каждый день
        scheduler.add_job(
            job_every_minute,
            trigger=CronTrigger(minute="*/1"),  # Every 1 minute
            # trigger=CronTrigger(second="*/10"),  # Every 1 minute
            id="job_every_minute",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
