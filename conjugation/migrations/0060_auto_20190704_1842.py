# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-04 15:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0059_pollyaudio_polly'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pollyaudio',
            name='datetime_creation',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='error',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='language_code',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='output_format',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='request_characters',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='sample_rate',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='task_id',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='task_status',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='text',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='text_type',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='url',
        ),
        migrations.RemoveField(
            model_name='pollyaudio',
            name='voice_id',
        ),
    ]
