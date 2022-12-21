# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-14 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0023_auto_20221214_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='do_not_display_to_paying_users',
            field=models.BooleanField(default=False, verbose_name='Do not display to users who ever payed'),
        ),
    ]