# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-14 18:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0024_lineitem_do_not_display_to_paying_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='display_to_paying_users',
            field=models.BooleanField(default=False, verbose_name='Display only to users who ever payed for lessons'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='do_not_display_to_paying_users',
            field=models.BooleanField(default=False, verbose_name='Do not display to users who ever payed for lessons'),
        ),
    ]