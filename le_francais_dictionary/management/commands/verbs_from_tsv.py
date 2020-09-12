from bulk_update.helper import bulk_update
from django.core.management import BaseCommand
import csv

from home.models import LessonPage
from le_francais_dictionary.models import Verb, VerbForm, VerbPacket, VerbPacketRelation, TENSE_CHOICES


def get_tense_id(name):
	for tense_id, tense_name in TENSE_CHOICES:
		if tense_name == name:
			return tense_id
	return None


class Command(BaseCommand):
	def handle(self, *args, **options):
		verb_translations_path = 'le_francais_dictionary/local/Verbs for cards - SMALL TABLE.csv'
		verb_forms_path = 'le_francais_dictionary/local/Verbs for cards - GRAND TABLE.csv'

		existed_packets = {packet.lesson.lesson_number:packet for packet in list(VerbPacket.objects.select_related('lesson').all())}
		existed_verbs = {verb.verb:verb for verb in list(Verb.objects.all())}
		existed_forms = {verb_form.form:verb_form for verb_form in list(VerbForm.objects.all())}
		VerbPacketRelation.objects.all().delete()

		verb_infinitives_file = open(verb_translations_path, 'r', encoding='utf-8')
		verb_infinitives_reader = csv.DictReader(verb_infinitives_file, dialect=csv.excel)

		infinitive_translation_map = {}
		for row in verb_infinitives_reader:
			infinitive = row['INFINITIVE']
			translation = row['TRANSLATION']
			translation_text = row['RU_SYNT']
			infinitive_translation_map[infinitive] = (translation, translation_text)

		verb_forms_file = open(verb_forms_path, 'r', encoding='utf-8')
		verb_forms_reader = csv.DictReader(verb_forms_file, dialect=csv.excel)

		forms_to_save = []
		verb_packet_relations_to_save = []

		verb_order = 0
		form_order = 0
		last_infinitive = None
		last_tense = None
		last_lesson_number = None
		lessons = {lesson.lesson_number: lesson for lesson in LessonPage.objects.all()}
		for row in verb_forms_reader:
			if not row['TRANSLATION'] or not row['LESSON_NO']:
				continue
			lesson_number = int(row['LESSON_NO'])
			if lesson_number in existed_packets.keys():
				packet = existed_packets[lesson_number]
			else:
				packet = VerbPacket(
					name=f'Глаголы урока {lesson_number}',
					lesson=lessons[lesson_number]
				)
				print(f'Saving Packet: {packet.name}')
				packet.save()
				existed_packets[lesson_number] = packet

			infinitive = row['VERBE']
			if infinitive in existed_verbs.keys():
				verb = existed_verbs[infinitive]
			elif infinitive in infinitive_translation_map.keys():
				verb = Verb(
					verb=row['VERBE'],
					type=Verb.TYPE_AFFIRMATIVE if row['TYPE'] == 'affirmative' else Verb.TYPE_NEGATIVE,
					regular=True if row['CLASS'] == 'regular' else False,
				)
				verb.translation, verb.translation_text = infinitive_translation_map[infinitive]
				print(f'Saving Verb: {verb.verb}')
				verb.save()
				existed_verbs[infinitive] = verb
			else:
				continue

			if lesson_number != last_lesson_number:
				verb_order = 0
			last_lesson_number = lesson_number

			tense = row['TENSE']
			if infinitive != last_infinitive or (infinitive == last_infinitive and tense != last_tense):
				verb_order += 1
				verb_packet_relations_to_save.append(VerbPacketRelation(
					packet=packet,
					verb=verb,
					order=verb_order,
					tense=get_tense_id(tense)
				))
				form_order = 0
			last_tense = tense
			last_infinitive = infinitive

			form_order += 1
			form_form = row['CONJUGAISON']

			if next((f for f in forms_to_save if f.form == form_form), None):
				continue

			if form_form in existed_forms.keys():
				form = existed_forms[form_form]
			else:
				form = VerbForm(form=form_form)
				existed_forms[form_form] = form

			form_to_show: str = row['CONJUGAISON']
			if form_to_show.find('ils') == 0:
				form_to_show = 'ils (elles)' + form_to_show[3:]
			elif form_to_show.find('il') == 0:
				form_to_show = 'il (elle, on)' + form_to_show[2:]

			form.verb = verb
			form.tense = get_tense_id(tense)
			form.order = form_order
			form.translation = row['TRANSLATION']
			form.translation_text = row['RU SYNTH']
			form.is_shown = row['IS_SHOWN'] if row['IS_SHOWN'] == '1' else False
			form.form_to_show = form_to_show
			forms_to_save.append(form)

		print(f'Saving Verb to Packets relations...')
		VerbPacketRelation.objects.bulk_create([rel for rel in verb_packet_relations_to_save if rel._state.adding])
		bulk_update([rel for rel in verb_packet_relations_to_save if not rel._state.adding])

		print(f'Saving verb Forms...')
		VerbForm.objects.bulk_create([form for form in forms_to_save if form._state.adding])
		bulk_update([form for form in forms_to_save if not form._state.adding])
