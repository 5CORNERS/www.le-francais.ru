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
    SAMPLE_RATE_CHOICES, PARAMS, FORMAT_LPCM, FILES_LE_FRANCAIS_PATH, FILE_EXTENSION, SAMPLE_RATE_48000, FORMAT_MP3
from yandex_speechkit.api import YandexAPI


# Create your models here.

class YandexSpeechKitTask(models.Model):
    text = models.CharField(max_length=5000, null=True, default=None, blank=True)
    ssml = models.CharField(max_length=5000, null=True, default=None, blank=True)
    lang = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, null=True, default=None)
    voice = models.CharField(max_length=10, choices=VOICES_CHOICES, null=True, default=None)
    emotion = models.CharField(max_length=10, choices=EMOTION_CHOICES, null=True, default=None)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, null=False, default=FORMAT_LPCM)
    sample_rate = models.CharField(max_length=10, choices=SAMPLE_RATE_CHOICES, null=True, default=SAMPLE_RATE_48000,
                                   blank=True)
    task_status = models.CharField(max_length=10, null=True, default='CREATED')
    error = models.BooleanField(default=False, blank=True)
    stream = models.BinaryField(null=True, default=None, blank=True)
    url = models.URLField(null=True, default=None, blank=True)
    error_message = models.TextField(null=True, default=None, blank=True)

    def get_filename(self, extension=None) -> str:
        if self.text:
            name = slugify(self.text, allow_unicode=True)
        else:
            name = slugify(re.sub(r"</?[^>]+>", "", self.ssml), allow_unicode=True)
        if extension is None:
            extension = FILE_EXTENSION[self.format]
        return f"{self.pk}_{name}.{extension}"

    def get_file(self) -> BytesIO:
        file = BytesIO()
        file.write(self.stream)
        file.seek(0)
        return file

    def get_segment(self) -> AudioSegment:
        file = self.get_file()
        if self.format == FORMAT_MP3:
            return AudioSegment.from_file(file, 'mp3')
        elif self.format == FORMAT_LPCM:
            return AudioSegment.from_raw(
                file,
                frame_rate=int(self.sample_rate),
                channels=1,
                sample_width=2,
            )
        else:
            return AudioSegment.from_file(file, format=FILE_EXTENSION[self.format])

    def to_dict(self) -> dict:
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            if not f.value_from_object(self) is None and f.name in PARAMS.keys():
                data[PARAMS[f.name]] = f.value_from_object(self)
        return data

    def synthesize(self) -> 'YandexSpeechKitTask':
        if self.pk is None:
            self.save()
        api = YandexAPI()
        stream, self.error, self.task_status, self.error_message = api.get_audio_stream(speechkit_task=self)
        if not self.error:
            self.stream = stream.read()
        else:
            self.stream = None
        self.save(update_fields=['stream', 'error', 'task_status', 'error_message'])
        return self

    def save_to_file(self, save_path=None, tags=None, result_task_status='saved'):
        if save_path is None:
            url = f"https://files.le-francais.ru/dictionary/speechkit/{self.get_filename(extension='mp3')}"
            save_path = f'/var/www/www-root/data/www/files.le-francais.ru/{FILES_LE_FRANCAIS_PATH}'
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
            self.url = url,
            self.stream = None
            self.task_status = result_task_status
            self.save(update_fields=['url', 'stream', 'task_status'])
        return self

    def start_task(self) -> None:
        try:
            self.synthesize()
            self.save_to_file()
        except Exception as e:
            self.error = True
            self.task_status = 'ERROR'
            self.save(update_fields=['error', 'task_status'])
            raise e

    def get_mp3(self, tags) -> BytesIO:
        file = BytesIO()
        if self.format == FORMAT_MP3:
            file.write(self.stream)
        else:
            if self.format == FORMAT_LPCM:
                audio_segment = AudioSegment.from_file(
                    self.get_file(),
                    'raw',
                    frame_rate=int(self.sample_rate),
                    channels=1,
                    sample_width=2,
                )
            else:
                audio_segment = AudioSegment.from_file(self.get_file(), format=FILE_EXTENSION[self.format])
            audio_segment.export(file, format="mp3", tags=tags if tags else {}, bitrate="192k")
        file.seek(0)
        return file


def combine_audio_streams(file1, file2, export_format="mp3"):
    stream1 = AudioSegment.from_mp3(file1)
    stream2 = AudioSegment.from_mp3(file2)
    combined_stream = stream1 + stream2
    output = BytesIO()
    combined_stream.export(output, format=export_format, bitrate="192k")
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


def create_joined_task_v2(*tasks, params, text=None, tags=None, save_path=None):
    segments = []
    for task, param in zip(tasks, params):
        task: YandexSpeechKitTask
        segment = task.get_segment()
        if 'level' in param.keys() and param['level']:
            segment = segment - 6
        segments.append(segment)

    result: AudioSegment = segments[0]
    for segment in segments[1:]:
        result += segment

    new_task = YandexSpeechKitTask()
    for attr in ["lang", "voice", "emotion", "format", "sample_rate"]:
        setattr(new_task, attr, getattr(tasks[0], attr))
    if text:
        new_task.text = text
    with BytesIO() as new_file:
        result.export(new_file, format="wav")
        new_file.seek(0)
        new_task.stream = new_file.read()

    new_task.save()
    new_task.save_to_file(save_path, tags=tags)
    return new_task
