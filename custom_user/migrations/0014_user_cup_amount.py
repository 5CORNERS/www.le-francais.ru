# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-31 16:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0013_user_payed_lessons'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cup_amount',
            field=models.IntegerField(default=0),
        ),
    ]
