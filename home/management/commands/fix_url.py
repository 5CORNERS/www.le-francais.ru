from urllib.parse import urlparse

from django.core.management import BaseCommand

from home.models import LessonPage


class Command(BaseCommand):
    def handle(self, *args, **options):
        for page in LessonPage.objects.all():
            page.summary = urlparse(page.summary).path
            page.repetition_material = urlparse(page.repetition_material).path
            page.save()
