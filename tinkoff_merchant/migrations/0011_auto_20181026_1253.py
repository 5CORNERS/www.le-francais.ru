# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-26 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tinkoff_merchant', '0010_auto_20181026_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='receiptitem',
            name='site_quantity',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='creation_date',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Дата создания заказа'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='success',
            field=models.BooleanField(default=False, editable=False, verbose_name='Без ошибок'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='update_date',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Дата последнего обновления'),
        ),
        migrations.AlterField(
            model_name='receiptitem',
            name='category',
            field=models.CharField(choices=[('coffee_cups', 'Чашки кофе'), ('lesson_tickets', 'Тикеты')], default='', max_length=20, verbose_name='Категория товара'),
        ),
    ]
