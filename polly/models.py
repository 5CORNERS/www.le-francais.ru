from django.db import models

from .const import *
from .api import PollyAPI

# Create your models here.


class PollyTask(models.Model):
	datetime_creation = models.DateTimeField(null=True, default=None, verbose_name='Дата создания')
	text = models.CharField(max_length=1024, null=True, default=None)
	text_type = models.CharField(max_length=4, choices=TEXT_TYPES, null=True, default=None)
	language_code = models.CharField(choices=LANGUAGE_CODES, null=True, default=None, max_length=16)
	output_format = models.CharField(choices=OUTPUT_FORMATS, null=True, default=None, max_length=16)
	sample_rate = models.CharField(choices=SAMPLE_RATES, null=True, default=None, max_length=16)
	voice_id = models.CharField(choices=VOICE_IDS, null=True, default=None, max_length=16)
	task_id = models.CharField(max_length=64, null=True, default=None)
	task_status = models.CharField(choices=TASK_STATUSES, null=True, default=None, max_length=16)
	request_characters = models.IntegerField(null=True, default=None)
	url = models.URLField(null=True, verbose_name='Ссылка на файл', default=None)
	error = models.BooleanField(default=False)

	def to_dict(self) -> dict:
		opts = self._meta
		data = {}
		for f in opts.concrete_fields:
			if not f.value_from_object(self) is None and f.name in PARAMS.keys():
				data[PARAMS[f.name]] = f.value_from_object(self)
		return data

	def create_task(self, output_s3_key_prefix, wait=False, save=False):
		api = PollyAPI(output_s3_key_prefix=output_s3_key_prefix)
		api.start_task(self, wait, save)

	def get_audio_stream(self, output_s3_key_prefix):
		api = PollyAPI(output_s3_key_prefix=output_s3_key_prefix)
		return api.get_audio_stream(self)
