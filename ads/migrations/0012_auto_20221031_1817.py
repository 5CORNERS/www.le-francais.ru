# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-10-31 15:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0011_lineitem_disable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='do_not_display_to_registered_users',
            field=models.BooleanField(default=False),
        ),
    ]