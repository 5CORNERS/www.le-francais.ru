# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-08 19:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0092_auto_20201008_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='audio_new',
            field=models.URLField(blank=True, default=None, null=True),
        ),
    ]
