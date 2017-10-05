from django.core.management import BaseCommand
from home.models import LessonPage, PageWithSidebar


class Command(BaseCommand):
	def handle(self, *args, **options):
		self.create_parents()
		self.move_pages()

	def create_parents(self):
		a1_target, created = PageWithSidebar.objects.get_or_create(
			path='0001000100090001',
			depth=4,
			title='A1_target',
			slug='A1_target',
			live=True,
			url_path='home/lecons_a1/A1_target',
			show_in_menus=False,
		)
		for i in range(5):
			season, created = PageWithSidebar.objects.get_or_create(
				path='00010001000A000' + str(i+1),
				numchild=1,
				depth=4,
				title='season_'+str(i+1),
				slug='season_'+str(i+1),
				live=True,
				url_path='home/lecons_b2/season_'+str(i+1),
				show_in_menus=True,
			)
			season_target, created = PageWithSidebar.objects.get_or_create(
				path='00010001000A000' + str(i + 1) + '0001',
				depth=5,
				title='season_' + str(i + 1) + '_target',
				slug='season_' + str(i + 1) + '_target',
				live=True,
				url_path='home/lecons_b2/season_' + str(i + 1)+'/season_'+ str(i + 1)+'_target',
				show_in_menus=False,
			)


	def move_pages(self):
		for page in LessonPage.objects.all():
			n = page.lesson_number
			target = None
			if 6 <= n <= 60:
				target = PageWithSidebar.objects.get(slug='A1_target')
			elif n >= 60:
				if n <= 113:
					target = PageWithSidebar.objects.get(slug='season_1_target')
				elif n <= 163:
					target = PageWithSidebar.objects.get(slug='season_2_target')
				elif n <= 217:
					target = PageWithSidebar.objects.get(slug='season_3_target')
				elif n <= 253:
					target = PageWithSidebar.objects.get(slug='season_4_target')
				elif n > 253:
					target = PageWithSidebar.objects.get(slug='season_5_target')
			if not target == None:
				page.move(target)
			else:
				pass

