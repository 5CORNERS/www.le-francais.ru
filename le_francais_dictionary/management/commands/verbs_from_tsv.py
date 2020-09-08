from bulk_update.helper import bulk_update
from django.core.management import BaseCommand
import csv

from django.db import transaction

from home.models import LessonPage
from le_francais_dictionary.models import Verb, VerbForm, VerbPacket


class Command(BaseCommand):
	def handle(self, *args, **options):
		verb_translations_path = 'le_francais_dictionary/local/Verbs for cards - SMALL TABLE.csv'
		verb_forms_path = 'le_francais_dictionary/local/Verbs for cards - GRAND TABLE.csv'
		infinitive_verb_map = {}
		existed_packets = {packet.name:packet for packet in list(VerbPacket.objects.all())}
		existed_verbs = {verb.verb:verb for verb in list(Verb.objects.all())}
		existed_forms = {verb_form.pk:verb_form for verb_form in list(VerbForm.objects.all())}
		with open(verb_translations_path, 'r', encoding='utf-8') as vt_f:
			verb_translations_reader = csv.DictReader(vt_f,
			                                          dialect=csv.excel)
			order = 0
			verbs_to_save = []
			for row in verb_translations_reader:
				order += 1
				verb = existed_verbs.get(row['INFINITIVE'], None)
				if verb is None:
					verb = Verb(
						verb=row['INFINITIVE']
					)
				print(verb.verb)
				verbs_to_save.append(verb)
				verb.translation = row['TRANSLATION']
				verb.translation_text = row['RU_SYNT']
				verb.order = order
				infinitive_verb_map[verb.verb] = verb
				verbs_to_save.append(verb)
			bulk_update([verb for verb in verbs_to_save if not verb._state.adding])
			Verb.objects.bulk_create([verb for verb in verbs_to_save if verb._state.adding])
		with open(verb_forms_path, 'r', encoding='utf-8') as vf_f:
			verbs_to_save = []
			verb_forms_to_save = []
			packets_to_save = []
			lessons = {lesson.lesson_number:lesson for lesson in LessonPage.objects.all()}
			verb_forms_reader = csv.DictReader(vf_f,
			                                          dialect=csv.excel)
			verb = None
			order = 0
			for row in verb_forms_reader:
				if not row['LESSON_NO']:
					continue
				if not row['TRANSLATION']:
					continue

				lesson = lessons[int(row['LESSON_NO'])]
				packet_name = f'Глаголы урока {lesson.lesson_number}'
				packet = existed_packets.get(
					packet_name, None
				)
				if packet is None:
					packet = VerbPacket(
						id=lesson.lesson_number,
						name=packet_name,
						lesson=lesson,
					)
					existed_packets[packet_name] = packet
					packets_to_save.append(packet)

				try:
					new_verb = infinitive_verb_map[row['VERBE']]
				except KeyError:
					continue
				if verb == new_verb:
					order += 1
				else:
					order = 1
					verb = new_verb
					verb.packet_id = packet.pk
					if row['TYPE'] == 'affirmative':
						verb.type = 0
					elif row['TYPE'] == 'negative':
						verb.type = 1
					if row['CLASS'] != 'regular':
						verb.regular = False
					verbs_to_save.append(verb)
				form_to_show:str = row['CONJUGAISON']
				if form_to_show.find('ils') == 0:
					form_to_show = 'ils (elles)' + form_to_show[3:]
				elif form_to_show.find('il') == 0:
					form_to_show ='il (elle, on)' + form_to_show[2:]
				verb_form = existed_forms.get(int(row['ID']), None)
				if verb_form is None:
					verb_form = VerbForm(
						id=int(row['ID']),
						verb_id=verb.pk,
						order=order,
						form=row['CONJUGAISON'],
						translation=row['TRANSLATION'],
						translation_text=row['RU SYNTH'],
						is_shown=row['IS_SHOWN'] if row['IS_SHOWN'] == '1' else False,
						form_to_show=form_to_show,
					)
				else:
					verb_form.verb_id = verb.pk
					verb_form.order = order
					verb_form.form = row['CONJUGAISON']
					verb_form.translation = row['TRANSLATION']
					verb_form.translation_text = row['RU SYNTH']
					verb_form.is_shown = row['IS_SHOWN'] if row['IS_SHOWN'] == '1' else False
					verb_form.form_to_show = form_to_show
					if verb.translation is None:
						continue
				verb_forms_to_save.append(verb_form)
				print(verb_form.form)
			VerbPacket.objects.bulk_create([packet for packet in packets_to_save if packet._state.adding])
			bulk_update([packet for packet in packets_to_save if not packet._state.adding])
			bulk_update(verbs_to_save)
			VerbForm.objects.bulk_create([form for form in verb_forms_to_save if form._state.adding])
			bulk_update([form for form in verb_forms_to_save if not form._state.adding])
