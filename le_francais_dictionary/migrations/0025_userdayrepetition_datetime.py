# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-16 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0024_userwordrepetition_repetition_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdayrepetition',
            name='datetime',
            field=models.DateTimeField(null=True),
        ),
    ]
