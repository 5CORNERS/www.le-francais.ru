# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-20 12:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_auto_20171220_1443'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AdBlock',
            new_name='AdvertCode',
        ),
    ]
