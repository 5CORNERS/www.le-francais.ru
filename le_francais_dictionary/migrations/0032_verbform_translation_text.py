# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-02 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0031_auto_20200423_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='verbform',
            name='translation_text',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
