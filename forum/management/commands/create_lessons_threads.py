import re
from datetime import datetime
import pytz

from django.conf import settings

import pandas as pd
from custom_user.models import User
from django.core.management import BaseCommand
from markdown import Markdown

from home.models import LessonPage
from pybb.models import Forum, Topic, Post


class Command(BaseCommand):
	# def add_arguments(self, parser):
	#     parser.add_argument('file_path', nargs='+', type=str)

	def handle(self, *args, **options):
		_parser = Markdown(
			extensions=[
				'forum.mdownx.nofollowlinks',
				'markdown.extensions.nl2br',
				'pymdownx.extra',
				'pymdownx.emoji',
				'pymdownx.tasklist',
				'pymdownx.details',
				'pymdownx.superfences',
				'pymdownx.details',
			],
			safe_mode='escape',
		)
		table = self.import_from_csv('narodny_konspekt.csv')
		for lesson_number in table:
			table[lesson_number] = self.rewrite(table[lesson_number])
			if isinstance(table[lesson_number], float):
				pass
			else:
				try:
					page = LessonPage.objects.get(lesson_number=lesson_number)
				except:
					self.stdout.write("Lesson page doesn't exist")
					break
				page.has_own_topic = True
				new_topic, topic_created = Topic.objects.get_or_create(
					forum=Forum.objects.get(name='Lessons Forum'),
					name='Урок-' + str(page.lesson_number),
					user=User.objects.get(username='ILYA'),
					slug='lecon' + str(page.lesson_number),
				)
				page.topic_id = new_topic.id
				self.stdout.write(str(lesson_number) + ' thread created')
				body = table[lesson_number]
				new_post = Post(
					body=body,
					topic_id=new_topic.id,
					user_id=new_topic.user_id,
					user_ip='1.1.1.1',
					created=datetime.now(tz=pytz.timezone(settings.TIME_ZONE)),
				)
				new_post.save()
				self.stdout.write(str(lesson_number) + ' post created')
				page.save()

	def create_other_threads(self):
		for page in LessonPage.objects.all():
			if not page.has_own_topic:
				new_topic, topic_created = Topic.objects.get_or_create(
					forum=Forum.objects.get(name='Lessons Forum'),
					name='Урок-' + str(page.lesson_number),
					user=User.objects.get(username='admin'),
					slug='lecon' + str(page.lesson_number),
				)
				if topic_created:
					page.topic_id = new_topic.id
					self.stdout.write(str(page.lesson_number) + ' thread created')
					body = 'Не стесняйтесь задавать вопросы и комментировать.'
					new_post = Post(
						body=body,
						topic_id=new_topic.id,
						user_id=new_topic.user_id,
						user_ip='1.1.1.1',
						created=datetime.now(),
					)
					new_post.save()
					self.stdout.write(str(lesson_number) + ' post created')
				else:
					self.stdout.write(str(lesson_number) + ' thread not created')
				page.save()

	def import_from_csv(self, fp):
		df = pd.read_csv(fp)
		table = df.to_dict()
		new_dict = {}
		for i in range(len(table['NUM'])):
			new_dict[table['NUM'][i]] = table['VAL'][i]
		table = new_dict
		return table

	def rewrite(self, line: str):
		new_line = str()
		if isinstance(line, str):
			for i in range(len(line) - 1):
				char = line[i]
				if (char == '.' or char == ',' or char == ';' or char == ':' or char == '!' or char == '?' or char == ')') \
						and not line[i + 1] == ' ':
					if not (line[i + 1] == '.') and not (re.match(r'[0-9]+', line[i + 1])):
						char = char + ' '
				if char == '(' and not line[i - 1] == ' ':
					char = ' ' + char
				if char == '-' and line[i - 1] == ' ' and line[i + 1] == ' ':
					char = '—'
				new_line = new_line + char
			return new_line
		else:
			return line
