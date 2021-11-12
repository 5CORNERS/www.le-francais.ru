# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-11-12 10:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0020_add-verbose-name'),
        ('home', '0101_auto_20211110_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='reference_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
        migrations.AddField(
            model_name='pagewithsidebar',
            name='reference_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]
