# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-04 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0052_auto_20180503_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagelayoutadvertisementsnippet',
            name='code',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
