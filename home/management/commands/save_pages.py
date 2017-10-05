from django.core.management import BaseCommand

from home.models import LessonPage
from wagtail.wagtailcore.models import PageRevision
from django.contrib.auth.models import User


class Command(BaseCommand):
	def handle(self, *args, **options):

		for page in LessonPage.objects.all():
			revisions = PageRevision.objects.filter(page=page.id)
			for revision in revisions:
				if revision.is_latest_revision():
					revision.publish()
					break