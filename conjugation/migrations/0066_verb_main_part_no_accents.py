# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-05 13:08
from __future__ import unicode_literals

from django.db import migrations, models
from unidecode import unidecode


def fill_main_part_no_accents(apps, schema):
    Verb = apps.get_model('conjugation', 'Verb')
    for verb in Verb.objects.all():
        verb.main_part_no_accents = unidecode(verb.main_part)
        verb.save(update_fields=['main_part_no_accents'])

class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0065_complete_verb_main_part'),
    ]

    operations = [
        migrations.AddField(
            model_name='verb',
            name='main_part_no_accents',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
        migrations.RunPython(fill_main_part_no_accents, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='verb',
            name='main_part_no_accents',
            field=models.CharField(max_length=64),
        ),
    ]
