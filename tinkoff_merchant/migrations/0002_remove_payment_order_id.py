# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-23 13:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tinkoff_merchant', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='order_id',
        ),
    ]
