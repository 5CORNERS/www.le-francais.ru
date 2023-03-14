# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-03-01 15:53
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import tinkoff_merchant.utils


class Migration(migrations.Migration):

    dependencies = [
        ('tinkoff_merchant', '0021_payment_request_history'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['creation_date'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='payment',
            name='redirect_due_date',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Срок жизни ссылки'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='request_history',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, encoder=tinkoff_merchant.utils.Encoder),
        ),
        migrations.AlterField(
            model_name='payment',
            name='response_history',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, encoder=tinkoff_merchant.utils.Encoder),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status_history',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, encoder=tinkoff_merchant.utils.Encoder),
        ),
    ]