# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-01-21 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0103_auto_20220121_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='next_lesson_button',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='lessonpage',
            name='previous_lesson_button',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
