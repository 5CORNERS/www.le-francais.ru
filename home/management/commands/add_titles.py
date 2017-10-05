from django.core.management import BaseCommand
from ._private import import_table
from home.models import LessonPage


class Command(BaseCommand):
    def handle(self, *args, **options):
        for page in LessonPage.objects.all():
            if page.seo_title != '':
                page.menu_title = page.title
                self.stdout.write('Lesson ' + str(page.lesson_number) + ' -- ' + 'Copied title "' + page.title + '" to menu title')
                page.title = page.seo_title
                self.stdout.write('Lesson ' + str(page.lesson_number) + ' -- ' + 'Copied seo title "' + page.seo_title + '" to title')
                page.save()
