# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-11-01 18:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0014_auto_20221101_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='ad_unit_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
