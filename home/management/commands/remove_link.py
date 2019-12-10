import re

from bs4 import BeautifulSoup
from django.core.management import BaseCommand

from home.models import LessonPage
from ._private import set_block

NUMBERS = [6, 7, 10, 14, 17, 20, 24, 25, 26, 31, 33, 37, 58, 53]

def body_links(lesson: LessonPage):
	if lesson.lesson_number in NUMBERS:
		return lesson
	for i in range(len(lesson.body.stream_data)):
		block = lesson.body.__getitem__(i)
		if block.block_type != 'html':
			continue
		soup = BeautifulSoup(block.value, "html.parser")
		pattern = re.compile('(?:https?:)?\/\/files\.le-francais\.ru\/lecons\/french-[0-9]{1,3}.mp3')
		a = soup.find('a', {'href': pattern})
		if a:
			if a.parent.name == 'div':
				div = a.parent
				div.extract()
				block.value = str(soup)
				print(block.value)
				set_block(i, block, lesson.body)
				return lesson
	return None


def mail_links(lesson):
	for i in range(len(lesson.mail_archive.stream_data)):
		block = lesson.mail_archive.__getitem__(i)
		if block.block_type != 'html':
			continue
		new_value, was_replaced = re.subn(
			'<a\s[^>]*(href=["\'](?:https?:)?//files\.le-francais\.ru/lecons/french-[0-9]{1,3}.mp3)["\'][^>]*>(.*?)</a>',
			r'\2',
			block.value,
			flags=re.DOTALL
		)
		if was_replaced:
			block.value = new_value
			set_block(i, block, lesson.mail_archive)
	return lesson


class Command(BaseCommand):

	def handle(self, *args, **options):  # TODO в уроках 6,10,14,17,20,24,25,26,31,33,37 ссылки в body удалить отдельно
		for lesson in LessonPage.objects.filter(lesson_number__lt=61):
			# print(lesson.lesson_number)
			new_lesson = body_links(lesson)
			if new_lesson:
				new_lesson.save_revision().publish()
