# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-01 09:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0076_auto_20190328_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adunit',
            name='size_mapping',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.Mapping'),
        ),
    ]
