from django.core.management import BaseCommand
from home.models import LessonPage
from ._private import del_block
import json
import time
from custom_user.models import User

def html_to_block(html):
    return {
        'type':"html",
        'value':html,
    }

def set_block(block, page:LessonPage):
    page.mail_archive.stream_data = [block]
    return page

def import_data(fp="Copy of Дополнительная информация к урокам  (1)/d.json"):
    return json.load(open(fp, 'r', encoding='utf-8'))

def get_latest_page(n):
    return LessonPage.objects.get(lesson_number=n)


def iterate_data(data:dict):
    pages = []
    for lesson_number, lesson_data in data.items():
        n = int(lesson_number)
        html = lesson_data['html']

        page = get_latest_page(n)
        block = html_to_block(html)
        set_block(block, page)

        pages.append(page)
    return pages

def save_revisions(pages):
    for page in pages:
        print(page.lesson_number)
        page.save_revision()

def publish_revisions(pages):
    for page in pages:
        print(page.lesson_number)
        page.get_latest_revision().publish()


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = import_data()
        new_pages = iterate_data(data)
        save_revisions(new_pages)
        publish_revisions(new_pages)