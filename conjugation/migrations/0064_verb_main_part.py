# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-04 16:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0063_auto_20200204_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='verb',
            name='main_part',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
