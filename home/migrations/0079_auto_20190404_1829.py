# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-04 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0078_auto_20190401_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inlineadvertisementsnippet',
            name='adunit_code',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='inlineadvertisementsnippet',
            name='adunit_sizes',
            field=models.CharField(blank=True, default='', max_length=500, null=True),
        ),
    ]
