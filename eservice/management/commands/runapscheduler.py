from django.core.management.base import BaseCommand
from eservice.services import run_standalone_scheduler


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        run_standalone_scheduler()
