# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-10-06 15:19
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0108_mapping_sizes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagelayoutadvertisementsnippet',
            name='sizes',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list),
        ),
    ]
