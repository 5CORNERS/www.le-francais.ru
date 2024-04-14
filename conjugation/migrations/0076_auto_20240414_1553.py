# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-04-14 15:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0075_auto_20230216_1710'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerbSEO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=258)),
                ('description', models.CharField(max_length=1024)),
                ('verb', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='conjugation.Verb')),
            ],
        ),
        migrations.AlterField(
            model_name='regle',
            name='text_fr',
            field=models.CharField(blank=True, default='', max_length=100000),
        ),
    ]
