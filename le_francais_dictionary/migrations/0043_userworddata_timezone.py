# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-12 01:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0042_userworddata_custom_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='userworddata',
            name='timezone',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
