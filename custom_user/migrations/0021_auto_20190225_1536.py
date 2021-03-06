# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-25 12:36
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0020_auto_20181222_0050'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saw_message_datetime',
            field=models.DateTimeField(default=None, null=True, verbose_name='Дата сообщения'),
        ),
        migrations.AlterField(
            model_name='user',
            name='_cup_amount',
            field=models.IntegerField(default=0, verbose_name='Кол-во чашек/билеткиов'),
        ),
        migrations.AlterField(
            model_name='user',
            name='_cup_credit',
            field=models.IntegerField(default=0, verbose_name='Кол-во "кредитных" чашек'),
        ),
        migrations.AlterField(
            model_name='user',
            name='_low_price',
            field=models.BooleanField(default=False, verbose_name='Статус пенсионера/студента'),
        ),
        migrations.AlterField(
            model_name='user',
            name='must_pay',
            field=models.BooleanField(default=True, help_text='Определяет, должен ли пользователь активировать урок для доступа к материалам', verbose_name='Должен платить'),
        ),
        migrations.AlterField(
            model_name='user',
            name='saw_message',
            field=models.BooleanField(default=False, help_text='Пользователь получил сообщение о системе активации уроков', verbose_name='Видел сообщение'),
        ),
        migrations.AlterField(
            model_name='user',
            name='used_usernames',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, editable=False, encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name='Used Usernames'),
        ),
    ]
