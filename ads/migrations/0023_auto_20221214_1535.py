# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-14 12:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0022_auto_20221213_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='placements_and',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='line_items_and', related_query_name='line_items_and_set', to='ads.Placement', verbose_name='Placements AND'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='placements_and_inverted',
            field=models.BooleanField(default=False, verbose_name='Exclude Placements AND'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='placements',
            field=models.ManyToManyField(blank=True, to='ads.Placement', verbose_name='Placements OR'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='placements_inverted',
            field=models.BooleanField(default=False, verbose_name='Exclude Placements OR'),
        ),
    ]
