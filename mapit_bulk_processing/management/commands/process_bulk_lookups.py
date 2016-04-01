import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from ...models import BulkLookup


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Processes all the bulk lookup jobs that need processing"

    def handle(self, *args, **options):
        for bulk_lookup in BulkLookup.objects.needs_processing():
            self.process_job(bulk_lookup)

    def process_job(self, bulk_lookup):
        try:
            with transaction.atomic():
                bulk_lookup.started = timezone.now()
                bulk_lookup.save()
                self.do_lookup(bulk_lookup)
                bulk_lookup.finished = timezone.now()
                bulk_lookup.save()
                self.send_success_email(bulk_lookup)
        except Exception, e:
            logger.exception(e)
            bulk_lookup.started = None
            bulk_lookup.finished = None
            bulk_lookup.error_count += 1
            bulk_lookup.last_error = timezone.now()
            bulk_lookup.save()

    def do_lookup(self, bulk_lookup):
        self.stdout.write(self.style.SUCCESS('doing lookup'))

    def send_success_email(self, bulk_lookup):
        self.stdout.write(self.style.SUCCESS('sending success email'))
