# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-22 09:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0067_backurls'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='without_sightbar',
            field=models.BooleanField(default=False),
        ),
    ]
