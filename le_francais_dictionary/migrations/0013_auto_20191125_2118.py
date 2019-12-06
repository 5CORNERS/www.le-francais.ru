# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-11-25 18:18
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0012_userstandalonepacket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstandalonepacket',
            name='packets',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=150),
        ),
    ]
