# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-11-25 18:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0012_auto_20191125_2118'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userstandalonepacket',
            old_name='packets',
            new_name='words',
        ),
    ]
