import os
import re
from io import BytesIO

import pysftp
from django.conf import settings
from django.db import models
from django.utils.text import slugify

from os import environ, pathsep, path
environ["PATH"] += pathsep + path.abspath(os.path.join(settings.BASE_DIR, "ffmpeg"))
from pydub import AudioSegment

from yandex_speechkit.consts import LANGUAGE_CHOICES, VOICES_CHOICES, EMOTION_CHOICES, FORMAT_CHOICES, \
    SAMPLE_RATE_CHOICES, PARAMS, FORMAT_MP3, FILES_LE_FRANCAIS_PATH, FILE_EXTENSION
from yandex_speechkit.api import YandexAPI


# Create your models here.

class YandexSpeechKitTask(models.Model):
    text = models.CharField(max_length=5000, null=True, default=None, blank=True)
    ssml = models.CharField(max_length=5000, null=True, default=None, blank=True)
    lang = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, null=True, default=None)
    voice = models.CharField(max_length=10, choices=VOICES_CHOICES, null=True, default=None)
    emotion = models.CharField(max_length=10, choices=EMOTION_CHOICES, null=True, default=None)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, null=False, default=FORMAT_MP3)
    sample_rate = models.CharField(max_length=10, choices=SAMPLE_RATE_CHOICES, null=True, default=None, blank=True)
    task_status = models.CharField(max_length=10, null=True, default='CREATED')
    error = models.BooleanField(default=False, blank=True)
    stream = models.BinaryField(null=True, default=None, blank=True)
    url = models.URLField(null=True, default=None, blank=True)

    def get_filename(self):
        if self.text:
            name = slugify(self.text, allow_unicode=True)
        else:
            name = slugify(re.sub(r"</?[^>]+>", "", self.ssml), allow_unicode=True)
        return f"{self.pk}_{name}.{FILE_EXTENSION[self.format]}"

    def get_file(self):
        file = BytesIO()
        file.write(self.stream)
        file.seek(0)
        return file

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            if not f.value_from_object(self) is None and f.name in PARAMS.keys():
                data[PARAMS[f.name]] = f.value_from_object(self)
        return data

    def synthesize(self):
        if self.pk is None:
            self.save()
        api = YandexAPI()
        stream, self.error, self.task_status = api.get_audio_stream(speechkit_task=self)
        self.stream = stream.read()
        self.save(update_fields=['stream', 'error', 'task_status'])

    def save_to_file(self):
        path = f'/var/www/www-root/data/www/files.le-francais.ru{FILES_LE_FRANCAIS_PATH}'
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        srv = pysftp.Connection(
            host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
            username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
            password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
            cnopts=cnopts
        )
        with srv.cd(path):
            filename = self.get_filename()
            with BytesIO() as file:
                file.write(self.stream)
                file.seek(0)
                srv.putfo(file, filename)
            self.url = f"https://files.le-francais.ru{FILES_LE_FRANCAIS_PATH}{filename}"
            self.stream = None
            self.status = 'SAVED'
            self.save(update_fields=['url', 'stream'])

    def start_task(self):
        try:
            self.synthesize()
            self.save_to_file()
        except Exception as e:
            self.error = True
            self.task_status = 'ERROR'
            self.save(update_fields=['error', 'task_status'])
            raise e


def combine_audio_streams(file1, file2, export_format="mp3"):
    stream1 = AudioSegment.from_mp3(file1)
    stream2 = AudioSegment.from_mp3(file2)
    combined_stream = stream1 + stream2
    output = BytesIO()
    combined_stream.export(output, format=export_format)
    output.seek(0)  # Reset the stream position
    return output.read()


# Refactored create_joined_task function
def create_joined_task(primary_task, secondary_task):
    # Create a new task
    new_task = YandexSpeechKitTask()

    # Assign shared task attributes dynamically
    for attr in ["lang", "voice", "emotion", "format", "sample_rate"]:
        setattr(new_task, attr, getattr(primary_task, attr))

    # Update text by joining texts of both tasks
    new_task.text = f"{primary_task.text} {secondary_task.text}"

    # Combine audio streams and assign the result
    new_task.stream = combine_audio_streams(primary_task.get_file(), secondary_task.get_file())

    # Save the task and return
    new_task.save()
    return new_task
