# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-25 09:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0018_remove_verb_has_reflexive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verb',
            name='reflexive_no_accents',
        ),
    ]
