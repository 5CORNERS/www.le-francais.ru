# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-28 12:17
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0006_auto_20211111_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='labels',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), blank=True, null=True, size=None),
        ),
    ]
