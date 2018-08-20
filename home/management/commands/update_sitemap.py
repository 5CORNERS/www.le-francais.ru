from django.core.management import BaseCommand
from wagtail.contrib.sitemaps.views import sitemap


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
