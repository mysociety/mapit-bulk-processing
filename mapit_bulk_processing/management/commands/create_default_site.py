from urlparse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.sites.models import Site


class Command(BaseCommand):
    """
    This command creates or updates the first entry in the sites
    database, with the domain set to the domain part of
    settings.SITE_BASE_URL
    """

    help = "Create or update site id 1 with the domain in SITE_BASE_URL"

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity'))
        if settings.SITE_BASE_URL and settings.SITE_NAME:
            if verbosity >= 2:
                msg = "settings.SITE_BASE_URL = %s\n" % settings.SITE_BASE_URL
                self.stdout.write(msg)
            base_domain = urlparse(settings.SITE_BASE_URL).netloc
            if not base_domain:
                msg = "settings.SITE_BASE_URL is not a valid fqdn."
                raise CommandError(msg)
            try:
                default_site = Site.objects.get(id=1)
                default_site.domain = base_domain
                default_site.name = settings.SITE_NAME
                default_site.save()
                if verbosity >= 1:
                    msg = "Updated Site id=1 to have name: " \
                          "{0}, domain: {1}\n".format(
                              settings.SITE_NAME,
                              base_domain
                          )
                    self.stdout.write(msg)
            except Site.DoesNotExist:
                Site.objects.create(
                    name=settings.SITE_NAME,
                    domain=base_domain
                )
                if verbosity >= 1:
                    msg = "Created Site id=1 to with name: " \
                          "{0}, domain: {1}\n".format(
                              settings.SITE_NAME,
                              base_domain
                          )
                    self.stdout.write(msg)
        else:
            msg = "settings.SITE_BASE_URL or settings.SITE_NAME have not " \
                  "been set"
            raise CommandError(msg)
