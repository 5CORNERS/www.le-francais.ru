# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-25 14:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0048_auto_20190219_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='translation',
            name='verb',
        ),
        migrations.DeleteModel(
            name='Translation',
        ),
    ]
