# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-07 20:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0089_wagtailpagenavtree'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexreviews',
            name='show_in_sidebar',
            field=models.BooleanField(default=True),
        ),
    ]