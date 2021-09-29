# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-09-29 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tinkoff_merchant', '0016_payment_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('NEW', 'NEW'), ('FORM_SHOWED', 'FORM_SHOWED'), ('DEADLINE_EXPIRED', 'DEADLINE_EXPIRED'), ('CANCELED', 'CANCELED'), ('PREAUTHORIZING', 'PREAUTHORIZING'), ('AUTHORIZING', 'AUTHORIZING'), ('AUTHORIZED', 'AUTHORIZED'), ('AUTH_FAIL', 'AUTH_FAIL'), ('REJECTED', 'REJECTED'), ('3DS_CHECKING', '3DS_CHECKING'), ('3DS_CHECKED', '3DS_CHECKED'), ('REVERSING', 'REVERSING'), ('PARTIAL_REVERSED', 'PARTIAL_REVERSED'), ('REVERSED', 'REVERSED'), ('CONFIRMING', 'CONFIRMING'), ('CONFIRMED', 'CONFIRMED'), ('REFUNDING', 'REFUNDING'), ('PARTIAL_REFUNDED', 'PARTIAL_REFUNDED'), ('REFUNDED', 'REFUNDED')], default='', editable=False, max_length=20, verbose_name='Статус транзакции'),
        ),
    ]