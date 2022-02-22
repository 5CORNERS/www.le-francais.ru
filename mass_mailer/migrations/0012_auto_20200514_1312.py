# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-14 10:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mass_mailer', '0011_usersfilter_do_not_send_to_comcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagelog',
            name='message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mass_mailer.Message'),
        ),
        migrations.AlterField(
            model_name='messagelog',
            name='recipient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]