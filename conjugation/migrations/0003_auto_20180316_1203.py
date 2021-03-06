# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-16 09:03
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0002_auto_20171219_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='conditional',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='template',
            name='imperative',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='template',
            name='indicative',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='template',
            name='infinitive',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='template',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='template',
            name='participle',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='template',
            name='subjunctive',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
    ]
