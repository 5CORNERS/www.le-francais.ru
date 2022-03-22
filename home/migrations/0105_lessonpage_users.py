# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-03-22 15:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0104_auto_20220121_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='users',
            field=models.ManyToManyField(through='home.UserLesson', to=settings.AUTH_USER_MODEL),
        ),
    ]
