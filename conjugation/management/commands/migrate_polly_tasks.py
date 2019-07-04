from django.core.management import BaseCommand
from conjugation.models import PollyAudio
from polly.models import PollyTask

class Command(BaseCommand):
	ATTRIBUTES = [
		"datetime_creation",
		"text",
		"text_type",
		"language_code",
		"output_format",
		"sample_rate",
		"voice_id",
		"task_id",
		"task_status",
		"request_characters",
		"url",
		"error",
	]
	def handle(self, *args, **options):
		for polly_audio in PollyAudio.objects.all():
			if polly_audio.polly is None:
				polly_task = PollyTask()
				for attr in self.ATTRIBUTES:
					setattr(polly_task, attr, getattr(polly_audio, attr))
				# polly_task.save()
				polly_audio.polly = polly_task
				# polly_audio.save()

