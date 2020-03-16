from django.core.management import BaseCommand
import csv

from home.models import LessonPage
from le_francais_dictionary.models import Verb, VerbForm, VerbPacket


class Command(BaseCommand):
	def handle(self, *args, **options):
		verb_translations_path = 'le_francais_dictionary/local/verb_translations.tsv'
		verb_forms_path = 'le_francais_dictionary/local/verb_forms.tsv'
		with open(verb_translations_path, 'r', encoding='utf-8') as vt_f:
			verb_translations_reader = csv.DictReader(vt_f,
			                                          dialect=csv.excel_tab)
			for row in verb_translations_reader:
				verb, verb_created = Verb.objects.get_or_create(
					verb=row['INFINITIF'],
				)
				verb.translation = row['TRANSLATION']
				verb.save()
		with open(verb_forms_path, 'r', encoding='utf-8') as vf_f:
			verb_forms_reader = csv.DictReader(vf_f,
			                                          dialect=csv.excel_tab)
			verb = None
			order = 0
			for row in verb_forms_reader:
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
					verb.save()
				packet_name = f'Глаголы урока {lesson.lesson_number}'
				if packet.name != packet_name:
					packet.name = packet_name
					packet.save()
				form_to_show:str = row['CONJUGATION']
				if form_to_show.find('ils') == 0:
					form_to_show = 'ils (elles)' + form_to_show[3:]
				elif form_to_show.find('il') == 0:
					form_to_show ='il (elle, on)' + form_to_show[2:]
				verb_form, verb_form_created = VerbForm.objects.get_or_create(
					id=int(row['ID']),
				)
				verb_form.verb = verb
				verb_form.order = order
				verb_form.form = row['CONJUGATION']
				verb_form.translation = row['TRANSLATION']
				verb_form.is_shown = row['IS_SHOWN'] if row['IS_SHOWN'] == '1' else False
				verb_form.form_to_show = form_to_show
				verb_form.save()
