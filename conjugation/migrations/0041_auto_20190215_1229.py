# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-15 09:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0040_auto_20190213_1422'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pollyaudio',
            old_name='link',
            new_name='url',
        ),
        migrations.AlterField(
            model_name='pollyaudio',
            name='datetime_creation',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата создания'),
        ),
    ]
