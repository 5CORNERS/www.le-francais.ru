# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-12 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0007_checknotifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='push_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='category',
            field=models.CharField(choices=[('LK', 'Likes'), ('RP', 'Replyes'), ('MG', 'Messages'), ('TP', 'Topics'), ('IR', 'Interval Repetitions')], max_length=10, null=True),
        ),
    ]
