# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-11-11 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0005_auto_20211110_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='creative',
            name='label',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='label',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
    ]
