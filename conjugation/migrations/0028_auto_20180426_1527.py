# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-26 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0027_auto_20180425_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='verb',
            name='africa',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='belgium',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='book',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='can_feminin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='can_passive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='can_reflexive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='conjugated_with_avoir',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='conjugated_with_etre',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='group_no',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_archaique',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_defective',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_frequent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_impersonal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_intransitive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_pronominal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_rare',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_second_form',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_slang',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='is_transitive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='verb',
            name='regle_id',
            field=models.IntegerField(default=200),
        ),
        migrations.AddField(
            model_name='verb',
            name='s_en',
            field=models.BooleanField(default=False),
        ),
    ]
