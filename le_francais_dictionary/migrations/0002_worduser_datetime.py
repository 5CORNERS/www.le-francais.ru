# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-09 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='worduser',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
    ]
