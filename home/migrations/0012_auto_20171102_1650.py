# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-02 13:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_auto_20171102_1648'),
    ]

    operations = [
        migrations.RenameField(
            model_name='indexreviews',
            old_name='review_text',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='indexreviews',
            old_name='review_url',
            new_name='url',
        ),
    ]
