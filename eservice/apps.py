import os
from time import sleep

from django.apps import AppConfig
from django.core.management import call_command

from config.settings import NEWSLETTERING_ENABLED


def start_newslettering():
    if NEWSLETTERING_ENABLED:
        sleep(2)
        if os.environ.get('RUN_MAIN'):
            # os.environ.get('RUN_MAIN') рабочий способ для запуска только ОДНОГО планировщика
            from eservice.services import run_application_scheduler
            run_application_scheduler()


class EserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eservice'

    def ready(self):
        start_newslettering()
