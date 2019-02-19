from django.core.management import BaseCommand

from conjugation.models import PollyAudio
from conjugation.polly import PollyAPI


class Command(BaseCommand):
	def handle(self, *args, **options):
		api = PollyAPI()
		tasks = list(PollyAudio.objects.all())
		for c, task in enumerate(tasks):
			print('\rUpdating... {0} in {1}'.format(c + 1, len(tasks)))
			api.update_task(task)
