# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-05 19:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0028_verbpacket_lesson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verbform',
            name='form',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='verbform',
            name='form_to_show',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='verbform',
            name='translation',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='verbform',
            name='verb',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='le_francais_dictionary.Verb'),
        ),
    ]
