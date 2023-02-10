from django.core.management import BaseCommand
from wagtail.core.models import PageRevision

from home.management.commands._private import set_block
from home.models import LessonPage


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('lesson_numbers', nargs='+', type=int,
                             help='One or more lesson numbers')

    def handle(self, *args, **options):
        all_lessons = {l.lesson_number:l for l in LessonPage.objects.all()}
        to_save = []
        for lesson_number in options['lesson_numbers']:
            changed = False
            lesson_page:LessonPage = all_lessons[lesson_number]
            for block_index, block in enumerate(lesson_page.body):
                if block.block_type == 'paragraph' and '<br/>' in block.value.source:
                    block.value.source = br2p(block.value.source)
                    set_block(block_index, block, lesson_page.body)
                    changed = True
            if changed:
                if lesson_page.has_unpublished_changes:
                    raise Exception(f'{lesson_page.lesson_number} has unpublished changes')
                to_save.append(lesson_page)

        for page_to_save in to_save:
            print(page_to_save)
            new_revision = page_to_save.save_revision()
            new_revision.publish()

def br2p(s:str) -> str:
    s.strip("   ﻿ ")
    if s.startswith('<div class="rich-text">') and s.endswith('</div>'):
        s = s.replace('<div class="rich-text">', '')
        s = s[:-6]
    if not s.startswith('<p>'):
        s = '<p>' + s
    if not s.endswith('</p>'):
        s = s + '</p>'
    return s.replace('<br/>', '</p><p>')
