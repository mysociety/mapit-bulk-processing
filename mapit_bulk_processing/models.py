import os
import csv
import itertools
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.conf import settings


class BulkLookupQuerySet(models.QuerySet):
    def needs_processing(self):
        """
        Bulk lookups that need processing:

        - Haven't already started
        - Have a payment charge from Stripe
        - Have failed less than 3 times already
        - Last failed more than 15 minutes ago (if they've ever failed)
        """
        retry_minutes = settings.CHARGE_RETRY_INTERVAL
        retry_time = timezone.now() - timedelta(minutes=retry_minutes)
        retry_count = settings.MAX_CHARGE_RETRIES
        return self.filter(
            started__isnull=True,
            stripe_charge__isnull=False,
            error_count__lt=retry_count,
        ).filter(
            models.Q(last_error__lt=retry_time) | models.Q(last_error=None)
        ).distinct()


class BulkLookup(models.Model):
    original_file = models.FileField(
        upload_to='original_files/%Y/%m/%d/',
        blank=False
    )
    output_file = models.FileField(
        upload_to='output_files/%Y/%m/%d/',
        blank=True
    )
    postcode_field = models.CharField(max_length=256, blank=True)
    output_options = models.ManyToManyField(
        'OutputOption',
        related_name='bulk_lookups',
        related_query_name='bulk_lookup'
    )
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    started = models.DateTimeField(blank=True, null=True)
    finished = models.DateTimeField(blank=True, null=True)
    last_error = models.DateTimeField(blank=True, null=True)
    error_count = models.IntegerField(default=0, blank=False)

    objects = BulkLookupQuerySet.as_manager()

    def __str__(self):
        return "{} - {} - {:%d %B %Y, %H:%I}".format(
            self.email,
            os.path.basename(self.original_file.name),
            self.created
        )

    def price_in_pence(self):
        return self.price() * 100

    def price(self):
        return self.num_rows() * 1

    def num_rows(self):
        return sum(1 for row in self.original_file_reader())

    def postcode_field_choices(self):
        return [(f, f) for f in self.field_names()]

    def field_names(self):
        return self.original_file_reader().fieldnames

    def example_rows(self):
        return itertools.islice(self.original_file_reader(), 25)

    def original_file_reader(self):
        return csv.DictReader(self.original_file)

    def paid(self):
        has_stripe_charge = False
        try:
            has_stripe_charge = (self.stripe_charge is not None)
        except StripeCharge.DoesNotExist:
            pass
        return has_stripe_charge

    def output_field_names(self):
        names = self.field_names()
        for option in self.output_options.all():
            names += option.output_field_names()
        return names

    def output_filename(self):
        original_filename = os.path.basename(self.original_file.name)
        return original_filename.rstrip(".csv") + "_output.csv"


class OutputOption(models.Model):
    name = models.CharField(max_length=256, blank=False)
    mapit_area_type = models.CharField(max_length=256, blank=False)

    def __str__(self):
        return self.name

    def output_field_names(self):
        return [
            "{0} - Name".format(self.name),
            "{0} - GSS Code".format(self.name),
            "{0} - MapIt Id".format(self.name)
        ]

    def get_from_mapit_response(self, response):
        """ Extract the right data from mapit's response JSON """
        fields = {f: "" for f in self.output_field_names()}
        for id, area in response['areas'].iteritems():
            if area['type'] == self.mapit_area_type:
                fields["{0} - Name".format(self.name)] = area['name']
                fields["{0} - GSS Code".format(self.name)] = area['codes']['gss']  # NOQA
                fields["{0} - MapIt Id".format(self.name)] = id
                break
        return fields


class StripeCharge(models.Model):
    # Named in a non-pythonic way to match the way Stripe sends it from it's
    # checkout javascript
    stripeToken = models.CharField(max_length=255, blank=False)
    bulk_lookup = models.OneToOneField(
        'BulkLookup',
        blank=False,
        related_name='stripe_charge'
    )
    amount = models.IntegerField(blank=False)

    def __str__(self):
        return self.stripeToken
