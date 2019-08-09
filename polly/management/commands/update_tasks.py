from django.core.management import BaseCommand
from polly.models import PollyTask
from polly.api import PollyAPI


class Command(BaseCommand):

	def handle(self, *args, **options):
		api = PollyAPI()
		for pt in PollyTask.objects.filter(datetime_creation=None):
			api.update_task(pt)
