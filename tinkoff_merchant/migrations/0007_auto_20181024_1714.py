# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-24 14:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tinkoff_merchant', '0006_receipt_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipt',
            name='user',
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tinkoff_receipts', to=settings.AUTH_USER_MODEL),
        ),
    ]
