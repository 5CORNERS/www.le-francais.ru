# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-11-14 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0019_log_utm_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='placements_inverted',
            field=models.BooleanField(default=False),
        ),
    ]