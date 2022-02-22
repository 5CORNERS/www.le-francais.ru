# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-30 12:22
from __future__ import unicode_literals

from django.db import migrations, models
import mass_mailer.models


class Migration(migrations.Migration):

    dependencies = [
        ('mass_mailer', '0017_auto_20211229_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersfilter',
            name='send_only_to_gmail',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='usersfilter',
            name='filters',
            field=mass_mailer.models.ChoiceArrayField(base_field=models.CharField(choices=[('0', 'Users w/o activations'), ('1', 'Users with payments'), ('2', 'Payments w/o activations'), ('3', 'Users, which payed for 1 cup only'), ('4', 'Users, which payed for more than 1 cups'), ('5', 'Users, which payed for 5 cups only'), ('6', 'Users, which payed for 10 cups only'), ('7', 'Users, which payed for 20 cups only'), ('8', 'Users, which payed for 50 cups only'), ('9', 'Users w/o payments'), ('10', 'Users with payments for 10 or less cups or tickets including 0')], max_length=12), blank=True, default=list, size=None),
        ),
    ]