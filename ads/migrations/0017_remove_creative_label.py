# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-10-11 18:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0016_auto_20220916_1846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creative',
            name='label',
        ),
    ]