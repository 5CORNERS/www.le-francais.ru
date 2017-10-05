from django.core.management import BaseCommand
from home.models import LessonPage

class Command(BaseCommand):

	def handle(self, *args, **options):
		for page in LessonPage.objects.all():
			if not page.slug == 'lecon-85-1':
				page.lesson_number = page.slug.split('lecon-', 1)[1]
				page.save()
