# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-12 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0093_lessonpage_audio_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='transcript_docx',
            field=models.FileField(blank=True, default=None, null=True, upload_to='home/transcripts'),
        ),
    ]
