# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-20 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_auto_20171220_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adblock',
            name='body',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='adblock',
            name='header',
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
