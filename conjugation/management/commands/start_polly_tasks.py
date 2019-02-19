from django.core.management import BaseCommand

from conjugation.models import Verb, PollyAudio
from conjugation.views import Table, Mood, Tense
from conjugation.polly import *


class Command(BaseCommand):
	def handle(self, *args, **options):
		api = PollyAPI()
		verbs = list(Verb.objects.prefetch_related('reflexiveverb').all().order_by('-count'))
		tasks = []
		for v in verbs:  # type: Verb
			for verb, gender, is_reflexive in v.get_all():
				table = Table(verb, gender, is_reflexive)  # type: Table
				print()
				for mood in table.moods:  # type: Mood
					for tense in mood.tenses:  # type: Tense
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
		api.bulk_start_task(tasks)
