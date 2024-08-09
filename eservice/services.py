from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from eservice.email import send
from eservice.models import Newsletter, AttemptsNewsletter


def run_standalone_scheduler():
    """
    Данная функция для запуска планировщика должна вызываться командной строки python manage.py runapscheduler,
    так как в ней используется BlockingScheduler, который работает сам по себе и может заблокировать основной поток
    (Как альтернатива, запуск через отдельный поток по примеру, но и в таком варианте есть проблемы)
            # from django.core.management import call_command
            # def callback():
            #     call_command('runapscheduler')
            #
            # from threading import Thread
            # thr = Thread(target=callback)
            # thr.start()
    """
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    add_jobs_executions(scheduler)


def run_application_scheduler():
    """
    Данная функция для запуска планировщика должна вызываться из веб приложения,
    так как в ней используется BackgroundScheduler, который опирается на основной процесс
    """
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    add_jobs_executions(scheduler)


def add_jobs_executions(scheduler):
    scheduler.add_job(
        job_every_minute,
        trigger='interval',
        minutes=1,
        id="job_every_minute",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True
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

    print("Запуск планировщика...")
    scheduler.start()


def job_every_minute():
    """
    Периодическая выполняемая задача
    """
    print("Новая минута...")

    newsletters = Newsletter.get_newsletters_ready_to_sent()
    for newsletter in newsletters:
        operation_result = send(newsletter)

        # При каждой отправке обновляем следующее время и статус рассылки
        newsletter.set_next_sent_datetime()
        newsletter.refresh_status()

        # Сохранение результатов рассылки
        AttemptsNewsletter.objects.create(
            newsletter=newsletter,
            date_time_last_sent=operation_result[0],
            status=operation_result[1],
            mail_server_response=operation_result[2],
            owner=newsletter.owner
        )


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    Задача по очистке логов выполнения каждую неделю
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
