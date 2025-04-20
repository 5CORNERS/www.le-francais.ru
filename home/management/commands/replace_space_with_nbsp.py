import re

from django.core.management import BaseCommand

from home.management.commands._private import set_block
from home.models import LessonPage

RE_REPLACE_SPACE_WITH_NBSP = [re.compile(r' (?=[!?;:»])'), re.compile(r'(?<=[«]) ')]
# RE_REPLACE_UNIX_LINE_BREAK = re.compile(r'\r\n')
# RE_ROW_START = re.compile(r'^-\s', re.MULTILINE)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for lesson in LessonPage.objects.all():
            changed = False
            for i in range(len(lesson.body.stream_data)):
                block = lesson.body.__getitem__(i)
                if block.block_type == 'paragraph':
                    for pattern in RE_REPLACE_SPACE_WITH_NBSP:
                        if pattern.search(block.value.source):
                            block.value.source = pattern.sub(' ', block.value.source)
                            changed = True
                    set_block(i, block, lesson.body)
            if changed:
                print(lesson.lesson_number)
                lesson.save_revision().publish()