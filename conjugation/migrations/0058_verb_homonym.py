# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-22 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0057_pollyaudio_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='verb',
            name='homonym',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
