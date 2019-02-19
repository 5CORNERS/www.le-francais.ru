# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-13 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0038_verb_pp_invariable'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollyAudio',
            fields=[
                ('key', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('link', models.URLField(null=True, verbose_name='Ссылка на файл')),
                ('datetime_creation', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
        ),
    ]
