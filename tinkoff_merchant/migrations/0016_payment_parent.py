# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-09-29 11:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tinkoff_merchant', '0015_auto_20210518_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tinkoff_merchant.Payment'),
        ),
    ]
