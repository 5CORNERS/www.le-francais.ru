# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-02 20:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20170525_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='audio_material',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
