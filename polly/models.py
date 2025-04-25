import os
import re
from io import BytesIO

import pysftp
from django.utils.text import slugify
from pydub import AudioSegment

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
    engine = models.CharField(choices=ENGINE_CHOICES, default=DEFAULT_ENGINE, max_length=16)

    stream = models.BinaryField(null=True, default=None, blank=True)

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

    def update_task(self):
        api = PollyAPI()
        api.update_task(polly_task=self)

    def get_audio_stream(self):
        api = PollyAPI()
        return api.get_audio_stream(self)

    def get_audio_stream_and_save(self):
        self.stream = self.get_audio_stream().read()
        self.save()
        return self

    def get_audio_segment(self):
        if self.stream:
            if self.output_format == OUTPUT_FORMAT_MP3:
                with BytesIO() as mp3_file:
                    mp3_file.write(self.stream)
                    mp3_file.seek(0)
                    return AudioSegment.from_mp3(mp3_file)
            elif self.output_format == OUTPUT_FORMAT_PCM:
                return AudioSegment.from_raw(
                    BytesIO(self.stream),
                    frame_rate=int(self.sample_rate),
                    channels=1,
                    sample_width=2,
                )
        return None

    def save_to_file(self, save_path=None, tags=None, result_task_status='saved'):
        if save_path is None:
            url = f"https://files.le-francais.ru/dictionary/polly/{self.get_filename(extension='mp3')}"
            save_path = f'/var/www/www-root/data/www/files.le-francais.ru/dictionary/polly/'
        else:
            url = f"https://files.le-francais.ru/{save_path}{self.get_filename(extension='mp3')}"
            save_path = f'/var/www/www-root/data/www/files.le-francais.ru/{save_path}'
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        srv = pysftp.Connection(
            host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
            username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
            password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
            cnopts=cnopts
        )
        srv.makedirs(save_path)
        with srv.cd(save_path):
            filename = self.get_filename(extension='mp3')
            file = self.get_mp3(tags)
            srv.putfo(file, filename)
            self.url = url
            self.stream = None
            self.task_status = result_task_status
            self.save(update_fields=['url', 'stream', 'task_status'])
        return self

    def get_filename(self, extension):
        if self.text_type == TEXT_TYPE_SSML:
            name = slugify(re.sub(r"</?[^>]+>", "", self.text), allow_unicode=True)
        else:
            name = slugify(self.text, allow_unicode=True)
        if extension is None:
            extension = FILE_EXTENSION[self.output_format]
        return f"{self.pk}_{name}.{extension}"

    def get_mp3(self, tags):
        mp3_file = BytesIO()
        self.get_audio_segment().export(mp3_file, format='mp3', tags=tags, bitrate='192k')
        return mp3_file


def join_polly_tasks(*tasks, params, text, tags=None, save_path=None):
    segments = []
    for task, param in zip(tasks, params):
        task: PollyTask
        segment = task.get_audio_segment()
        if 'level' in param.keys() and param['level']:
            segment = segment - 6
        segments.append(segment)

    result: AudioSegment = segments[0]
    for segment in segments[1:]:
        result += segment

    new_task = PollyTask()
    for attr in ['text_type',
                 'language_code',
                 'output_format',
                 'sample_rate',
                 'voice_id',
                 'task_id']:
        setattr(new_task, attr, getattr(tasks[0], attr))

    new_task.text = text
    with BytesIO() as new_file:
        result.export(new_file, format="raw")
        new_file.seek(0)
        new_task.stream = new_file.read()

    new_task.save()
    new_task.save_to_file(save_path=save_path, tags=tags)

    return new_task
