# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-16 12:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0021_auto_20191216_1511'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userdayrepetition',
            old_name='words_ids',
            new_name='repetitions',
        ),
    ]
