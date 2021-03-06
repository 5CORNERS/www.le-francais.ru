# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-06-21 19:59
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0067_auto_20200424_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='verb',
            name='can_be_pronoun',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='template',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='template',
            name='new_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
    ]
