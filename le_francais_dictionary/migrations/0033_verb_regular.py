# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-02 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0032_verbform_translation_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='verb',
            name='regular',
            field=models.BooleanField(default=True),
        ),
    ]
