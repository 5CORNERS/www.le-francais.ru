from django.core.management import BaseCommand
from itertools import chain
from home.models import LessonPage, PageWithSidebar


class Command(BaseCommand):
    def handle(self, *args, **options):
        lessons_b2 = list(chain(LessonPage.objects.filter(path__startswith="000100010005"), PageWithSidebar.objects.filter(path__startswith="000100010005")))
        for page in lessons_b2:
            page.specific.page_type = 'article_page'
            print(page.title)
            page.save()