# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-29 14:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_auto_20210902_0450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='target',
            field=models.PositiveSmallIntegerField(choices=[(1, 'на хлеб насущный'), (2, 'на рекламу проекта'), (3, 'на дооснащение студии')], default=1),
        ),
    ]
