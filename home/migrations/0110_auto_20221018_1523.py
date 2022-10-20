# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-10-18 12:23
from __future__ import unicode_literals

from django.db import migrations
import home.blocks.LeFrancaisAdUnit
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0109_auto_20221006_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mapping',
            name='sizes',
            field=wagtail.core.fields.StreamField([('sizes', wagtail.core.blocks.StructBlock([('type', wagtail.core.blocks.ChoiceBlock(choices=[('v', 'viewport size greater than'), ('c', 'parent container size greater than or equal')], required=False)), ('window_or_container_size', wagtail.core.blocks.CharBlock(help_text='320x0 (width greater or equal than 320 and height greater or equal then 0)', required=False)), ('sizes', wagtail.core.blocks.ListBlock(home.blocks.LeFrancaisAdUnit.SimpleSizeBlock))]))], blank=True),
        ),
    ]
