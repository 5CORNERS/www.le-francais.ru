# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-06-10 14:18
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0106_auto_20220607_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagelayoutadvertisementsnippet',
            name='sizes',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list),
        ),
    ]