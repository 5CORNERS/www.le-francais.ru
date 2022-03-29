# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-03-28 18:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0035_auto_20200423_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, default=None, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='country_code',
            field=models.CharField(blank=True, default=None, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='country_name',
            field=models.CharField(blank=True, default=None, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='region',
            field=models.CharField(blank=True, default=None, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='logmessage',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='last name'),
        ),
    ]