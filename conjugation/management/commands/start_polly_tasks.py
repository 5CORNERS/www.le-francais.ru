from django.core.management import BaseCommand

from conjugation.models import Verb, PollyAudio
from conjugation.views import Table, Mood, Tense
from conjugation.polly import *


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('count', nargs='?', type=int, default=2)

	def handle(self, *args, **options):
		api = PollyAPI()
		verbs = list(Verb.objects.prefetch_related('reflexiveverb').all().order_by('-count'))[:options['count']]
		tasks = []
		print()
		for counter, v in enumerate(verbs):  # type: int, Verb
			print('\rCreating ssml texts... {0} in {1}'.format(counter+1, options['count']), end='')
			for verb, gender, is_reflexive in v.get_all():
				table = Table(verb, gender, is_reflexive)  # type: Table
				for mood in table.moods:  # type: Mood
					for tense in mood.tenses:  # type: Tense
						if tense.is_empty():
							continue
						polly_audio, created = PollyAudio.objects.get_or_create(key=tense.key)
						new_text = tense.get_polly_ssml()
						if created or polly_audio.url is None or polly_audio.text != new_text:
							polly_audio.text = new_text
							polly_audio.text_type = TEXT_TYPE_SSML
							polly_audio.language_code = LANGUAGE_CODE_FR
							polly_audio.sample_rate = SAMPLE_RATE_22050
							polly_audio.voice_id = VOICE_ID_LEA
							polly_audio.output_format = OUTPUT_FORMAT_MP3
							tasks.append(polly_audio)
		print()
		api.bulk_start_task(tasks)
		print('Done!')
