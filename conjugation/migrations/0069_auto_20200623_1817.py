# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-06-23 15:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0068_auto_20200621_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollyaudio',
            name='key',
            field=models.CharField(max_length=128, primary_key=True, serialize=False),
        ),
    ]
