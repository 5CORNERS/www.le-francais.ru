import re

from django.core.management import BaseCommand

from home.models import InlineAdvertisementSnippet
from home.models import LessonPage

PATH = '''C:\\Users\\ilia.dumov\\PycharmProjects\\www.le-francais.ru\\html_files\\'''


def get_snippet_name(value, page_type):
    if page_type == 'lesson_a1':
        value = 'lesson_a1/' + value
    elif page_type=='lesson_a2':
        value = 'lesson_a2/' + value
    elif page_type=='lesson_b2':
        value = 'lesson_b2/' + value
    return value


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('arg', type=int, nargs='+')
        pass
    def handle(self, *args, **options):
        for page in LessonPage.objects.all():
          if options['arg'][0] <= page.lesson_number <= options['arg'][1]:
            page_type = page.page_type
            new_body = []
            for stream_child in page.body.__iter__():
                if stream_child.block_type == 'html':
                    values = re.split('^<!--INLINE_SNIPPET_([0-9a-zA-Z]+?)-->$', str(stream_child.value), flags=re.M)
                    for value in values:
                        if value == '' or re.match('^\s+?$',value,re.M):
                            continue
                        elif value == '1' or value == '2' or value == '3':
                            snippet_name = get_snippet_name(value, page.page_type)
                            new_body.append((
                                'advertisement', {
                                    'advertisement': InlineAdvertisementSnippet.objects.get(name=snippet_name),
                                    'disable': False
                                }
                            ))
                        else:
                            new_body.append(('html', value))
                else:
                    new_body.append((stream_child.block_type, stream_child.value))
            page.body = new_body
            print(page.title + '\t-\tSaving draft',end='')
            page.save_revision()
            print('\t-\tPublishing', end='')
            page.get_latest_revision().publish()
            print('\t-\tDone')
