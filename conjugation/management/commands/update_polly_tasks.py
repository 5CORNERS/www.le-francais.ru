from django.core.management import BaseCommand

from conjugation.models import PollyAudio
from conjugation.polly import PollyAPI
from conjugation.views import Tense
from conjugation.polly import COMPLETED, FAILED


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('key', nargs='?', type=str)

	def handle(self, *args, **options):
		api = PollyAPI()
		if options['key']:
			tasks = [PollyAudio.objects.get(key=options['key'])]
		else:
			tasks = list(PollyAudio.objects.all())
		to_recreate = []
		for c, task in enumerate(tasks):
			print('\rChecking... {0} in {1}, {2} needs recreating'.format(c + 1, len(tasks), len(to_recreate)), end='')
			tense = Tense(key=task.key)
			if task.text != tense.get_polly_ssml() or task.task_status == FAILED:
				task.text = tense.get_polly_ssml()
				to_recreate.append(task)
		print()
		api.bulk_start_task(to_recreate)

