# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-10 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('le_francais_dictionary', '0036_auto_20200912_2300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verbform',
            name='tense',
            field=models.IntegerField(choices=[(0, 'Indicatif Présent'), (1, 'Passé Composé'), (2, 'Impératif Présent'), (3, 'Imparfait'), (4, 'Futur simple')], default=None, null=True),
        ),
        migrations.AlterField(
            model_name='verbpacketrelation',
            name='tense',
            field=models.IntegerField(choices=[(0, 'Indicatif Présent'), (1, 'Passé Composé'), (2, 'Impératif Présent'), (3, 'Imparfait'), (4, 'Futur simple')], default=0),
        ),
        migrations.AlterField(
            model_name='word',
            name='word_ssml',
            field=models.CharField(blank=True, default=None, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='wordtranslation',
            name='translations_ssml',
            field=models.CharField(blank=True, default=None, max_length=1000, null=True),
        ),
    ]
