from django.core.management import BaseCommand

from home.models import LessonPage, PageWithSidebar


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass