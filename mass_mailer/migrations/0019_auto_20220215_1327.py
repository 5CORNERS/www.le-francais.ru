# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-02-15 10:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mass_mailer', '0018_auto_20211230_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersfilter',
            name='manual_email_list',
            field=models.TextField(blank=True, default=None, help_text='Comma-separated list of emails, for testing purposes.', null=True),
        ),
    ]
