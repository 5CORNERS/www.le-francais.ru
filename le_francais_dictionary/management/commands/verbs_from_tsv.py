from django.core.management import BaseCommand
import csv

from home.models import LessonPage
from le_francais_dictionary.models import Verb, VerbForm, VerbPacket


class Command(BaseCommand):
	def handle(self, *args, **options):
		verb_translations_path = 'le_francais_dictionary/local/Verbs for cards - SMALL TABLE.csv'
		verb_forms_path = 'le_francais_dictionary/local/Verbs for cards - Verbs for cards - GRAND TABLE.csv'
		with open(verb_translations_path, 'r', encoding='utf-8') as vt_f:
			verb_translations_reader = csv.DictReader(vt_f,
			                                          dialect=csv.excel)
			for row in verb_translations_reader:
				verb, verb_created = Verb.objects.get_or_create(
					verb=row['INFINITIVE'],
				)
				if not verb_created and (verb.translation != row['TRANSLATION'] or verb.translation_text != row['VOICE']):
					verb.translation = row['TRANSLATION']
					verb.translation_text = row['VOICE']
					verb.save()
				else:
					pass
		with open(verb_forms_path, 'r', encoding='utf-8') as vf_f:
			verb_forms_reader = csv.DictReader(vf_f,
			                                          dialect=csv.excel)
			verb = None
			order = 0
			for row in verb_forms_reader:
				if not row['LESSON_NO']:
					continue
				lesson = LessonPage.objects.get(lesson_number=int(row['LESSON_NO']))
				packet, created_packet = VerbPacket.objects.get_or_create(
					lesson=lesson
				)
				new_verb, new_verb_created = Verb.objects.get_or_create(
					verb=row['VERBE'])
				if verb == new_verb:
					order += 1
				else:
					order = 1
					verb = new_verb
					verb.packet = packet
					if row['TYPE'] == 'affirmative':
						verb.type = 0
					elif row['TYPE'] == 'negative':
						verb.type = 1
					if row['CLASS'] != 'regular':
						verb.regular = False
					verb.save()
				packet_name = f'Глаголы урока {lesson.lesson_number}'
				if packet.name != packet_name:
					packet.name = packet_name
					packet.save()
				form_to_show:str = row['CONJUGAISON']
				if form_to_show.find('ils') == 0:
					form_to_show = 'ils (elles)' + form_to_show[3:]
				elif form_to_show.find('il') == 0:
					form_to_show ='il (elle, on)' + form_to_show[2:]
				verb_form, verb_form_created = VerbForm.objects.get_or_create(
					id=int(row['ID']),
				)
				verb_form.verb = verb
				verb_form.order = order
				verb_form.form = row['CONJUGAISON']
				verb_form.translation = row['TRANSLATION']
				verb_form.translation_text = row['RU SYNTH']
				verb_form.is_shown = row['IS_SHOWN'] if row['IS_SHOWN'] == '1' else False
				verb_form.form_to_show = form_to_show
				verb_form.save()
