import re

from django.core.management import BaseCommand
from pybb.models import Topic, Post

from home.models import LessonPage


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.add_links()

    def add_links(self):
        topics = Topic.objects.filter(forum__name='Комментируем уроки французского')
        start = False
        for topic in topics:
            if start == True:
                first_post = topic.head
                link = LessonPage.objects.get(lesson_number=self.get_num(topic)).get_url()
                markup = '[На страницу урока]' + '(' + link + ' \"' + topic.name + '\").'
                first_post.body += '\n\n' + markup
                print(topic.name)
                first_post.save()
            else:
                if topic.name == 'Урок 242':
                    start = True

    def get_num(self, topic):
        num = re.findall(r'[0-9]+', topic.name)
        return int(num[0])
