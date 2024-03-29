# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-07 14:01
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0073_verb_is_etre_verb'),
    ]

    operations = [
        migrations.AddField(
            model_name='verb',
            name='html_sizes',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='verb',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='conjugation.Template'),
        ),
    ]
