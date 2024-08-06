from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from eservice.email import send
from eservice.models import Newsletter, AttemptsNewsletter


def job_every_minute():
    print("Новая минута...")

    newsletters = Newsletter.get_newsletters_ready_to_sent()
    for newsletter in newsletters:
        operation_result = send(newsletter)

        newsletter.set_next_sent_datetime()
        newsletter.refresh_status()

        AttemptsNewsletter.objects.create(
            newsletter=newsletter,
            date_time_last_sent=operation_result[0],
            status=operation_result[1],
            mail_server_response=operation_result[2]
        )


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def run_standalone_scheduler():
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        job_every_minute,
        trigger=CronTrigger(minute="*/1"),  # Every 1 minute
        # trigger=CronTrigger(second="*/10"),  # Every 1 minute
        id="job_every_minute",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True,
    )
    print("Добавлена новая задача")

    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
            day_of_week="mon", hour="00", minute="00"
        ),  # Midnight on Monday, before start of the next work week.
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    print("Добавлена еженедельная задача удаления старых данных")

    try:
        print("Запуск планировщика...")
        scheduler.start()
    except KeyboardInterrupt:
        print("Остановка планировщика...")
        scheduler.shutdown()
        print("Планировщик успешно остановлен!")


def run_application_scheduler():
    """Данная функция для запуска планировщика должна вызываться из веб приложения,
    так как в ней используеютися BackgroundScheduler, который опирается на """
    DjangoJobExecution.objects.delete_old_job_executions(0)
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_every_minute, 'interval', minutes=1)
    # scheduler.add_job(f,
    #                   trigger=CronTrigger(minute="*/1"),  # Every 1 minute)
    #                   id="job_every_minute",  # The `id` assigned to each job MUST be unique
    #                   max_instances=1,
    #                   replace_existing=True,
    #                   )
    scheduler.start()
