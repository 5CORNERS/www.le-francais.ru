# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-07 14:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0052_auto_20190307_1608'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fr2rutranslation',
            name='children',
        ),
        migrations.RemoveField(
            model_name='fr2rutranslation',
            name='order',
        ),
    ]
