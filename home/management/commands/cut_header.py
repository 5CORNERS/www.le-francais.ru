from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from ._private import set_block, del_block, merge_blocks
from home.models import LessonPage, DefaultPage, PageWithSidebar


class Command(BaseCommand):
	def handle(self, *args, **options):
		self.pop_audio(LessonPage)

	def pop_audio(self, page_model):
		for page in page_model.objects.all():
			if 2 < page.lesson_number < 134:
				self.stdout.write(str(page.lesson_number))
				if page.lesson_number == 133:
					self.stdout.write('STOP!!!')
					break
				merge_blocks(0, 1, page.body)
				page.save()
