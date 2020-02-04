# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def complete_main_part(apps, schema_editor):
	Verb = apps.get_model('conjugation', 'Verb')
	for verb in Verb.objects.select_related('template').all():
		verb.main_part = verb.infinitive.rsplit(verb.template.name.split(':')[1], 1)[0]
		verb.save(update_fields=['main_part'])


class Migration(migrations.Migration):
	dependencies = [
		('conjugation', '0064_verb_main_part'),
	]

	operations = [
        migrations.RunPython(complete_main_part,
                             reverse_code=migrations.RunPython.noop),
		migrations.AlterField(
			model_name='verb',
			name='main_part',
			field=models.CharField(max_length=64),
		),
	]
