# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-01-23 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mass_mailer', '0023_auto_20230118_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersfilter',
            name='cups_amount_gte',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
