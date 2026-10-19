"""
Sync verbs, verb forms and verb packets with the "Verbs for cards" tables.

* SMALL TABLE -- infinitive translations (Verb.translation / translation_text).
* GRAND TABLE -- conjugated forms (VerbForm) plus verb type / class; more tables
                 with the same columns (ID optional) can be appended with --join.
* RELATIONS   -- which verb/tense goes to which packet (lesson) and in what order.

Records are matched and updated in place, so primary keys (used in the verbs app
URLs) and generated audio survive a re-import. Nothing is deleted unless --prune
is given; use --dry-run to preview the changes and --report to save the list of
skipped and stale rows to a text file.
"""
import csv
import glob
import os
import sys
from collections import Counter, OrderedDict, defaultdict
from itertools import chain

from bulk_update.helper import bulk_update
from django.core.management import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from home.models import LessonPage
from le_francais_dictionary.consts import TENSE_CHOICES, \
	TYPE_AFFIRMATIVE, TYPE_NEGATIVE
from le_francais_dictionary.models import Verb, VerbForm, VerbPacket, VerbPacketRelation

DEFAULT_DIR = 'le_francais_dictionary/local'
SMALL_TABLE = 'Verbs for cards - SMALL TABLE.csv'
GRAND_TABLE = 'Verbs for cards - GRAND TABLE.csv'
RELATIONS_TABLE = 'Verbs for cards - RELATIONS.csv'

# 'Futur simple' and 'Futur Simple' are both used in the tables
TENSE_IDS = {name.lower(): tense_id for tense_id, name in TENSE_CHOICES}

# Columns every forms table (GRAND TABLE and --join tables) must have; ID, LESSON_NO and IS_SHOWN are optional
FORM_TABLE_COLUMNS = ['VERBE', 'TYPE', 'CLASS', 'TENSE', 'CONJUGAISON', 'TRANSLATION', 'RU SYNTH']

FORM_FIELDS = ['verb_id', 'tense', 'order', 'is_shown', 'form_to_show', 'translation', 'translation_text']

SKIPPED_INFINITIVES = 'Infinitives skipped (in GRAND TABLE, missing from SMALL TABLE)'
SKIPPED_GRAND_ROWS = 'Forms table rows skipped (GRAND TABLE and joined tables, line numbers are CSV lines)'
DUPLICATE_FORMS = 'Forms listed more than once (first one is used) and how the rows differ'
# Columns that end up in the database; LESSON_NO / ID are expected to differ between duplicates
DUPLICATE_COMPARED_COLUMNS = ['TYPE', 'CLASS', 'IS_SHOWN', 'TRANSLATION', 'RU SYNTH']
SKIPPED_RELATIONS = 'RELATIONS rows skipped (line numbers are CSV lines)'
RELATIONS_WITHOUT_FORMS = 'RELATIONS rows with no forms in the forms tables'
STALE_RELATIONS = 'Stale relations (in the database: not in RELATIONS, or an extra copy of another relation)'
TO_VOICE = 'To be voiced with --revoice (French audio and Russian translation audio are regenerated)'
STALE_FORMS = 'Stale forms (in the database, not matched to the forms tables) and the packets showing them'
REPORT_SECTIONS = [SKIPPED_INFINITIVES, SKIPPED_GRAND_ROWS, DUPLICATE_FORMS, SKIPPED_RELATIONS,
				   RELATIONS_WITHOUT_FORMS, STALE_RELATIONS, STALE_FORMS, TO_VOICE]
# Duplicates are only counted on the console (there are hundreds); the full list is in --report
WARNING_SECTIONS = [SKIPPED_INFINITIVES, SKIPPED_GRAND_ROWS, SKIPPED_RELATIONS, RELATIONS_WITHOUT_FORMS]


def get_tense_id(name):
	return TENSE_IDS.get(name.strip().lower())


def read_table(path, required=()):
	"""Read a CSV table; every row gets its file name and line number in '_source' / '_line'."""
	if not os.path.exists(path):
		raise CommandError(f'File not found: {path}')
	with open(path, 'r', encoding='utf-8', newline='') as f:
		reader = csv.DictReader(f, dialect=csv.excel)
		missing = [column for column in required if column not in (reader.fieldnames or [])]
		if missing:
			raise CommandError(f'{path}: missing columns {", ".join(missing)}')
		rows = list(reader)
	for line, row in enumerate(rows, start=2):
		row['_source'], row['_line'] = os.path.basename(path), line
	return rows


def expand_paths(table_dir, pattern):
	"""A --join value: a file or a glob pattern, absolute or relative to the tables directory."""
	pattern = os.path.join(table_dir, pattern)
	if not glob.has_magic(pattern):
		return [pattern]
	paths = sorted(glob.glob(pattern))
	if not paths:
		raise CommandError(f'No files match {pattern}')
	return paths


def cell(row, column):
	"""Stripped value of an optional column (joined tables have no ID)."""
	return (row.get(column) or '').strip()


def get_form_to_show(form):
	if form.startswith('ils'):
		return 'ils (elles)' + form[3:]
	if form.startswith('il'):
		return 'il (elle, on)' + form[2:]
	return form


def format_ranges(numbers):
	"""[3, 4, 5, 9] -> '3-5, 9'"""
	ranges = []
	for number in sorted(numbers):
		if ranges and number == ranges[-1][1] + 1:
			ranges[-1][1] = number
		else:
			ranges.append([number, number])
	return ', '.join(str(a) if a == b else f'{a}-{b}' for a, b in ranges)


class Command(BaseCommand):
	help = 'Import verbs, verb forms and packet relations from the "Verbs for cards" CSV tables'

	def add_arguments(self, parser):
		parser.add_argument('--dir', dest='dir', default=DEFAULT_DIR,
							help=f'Directory with the CSV tables (default: {DEFAULT_DIR})')
		parser.add_argument('--join', dest='join', action='append', default=[], metavar='FILE',
							help='Extra forms table appended to GRAND TABLE: a file or glob pattern, absolute or '
								 'relative to --dir (repeatable; when tables list the same form, the first one wins)')
		parser.add_argument('--dry-run', action='store_true', dest='dry_run',
							help='Show what would change and roll everything back')
		parser.add_argument('--prune', action='store_true', dest='prune',
							help='Delete forms and packet relations that are no longer in the tables')
		parser.add_argument('--report', dest='report',
							help='Write skipped and stale infinitives, forms and relations to this text file')
		parser.add_argument('--only-differences', action='store_true', dest='only_differences',
							help='Leave duplicate forms with no difference out of the report (they are still counted)')
		parser.add_argument('--check-voice', action='store_true', dest='check_voice',
							help='Only check that voicing can run (credentials, Google TTS voices, SFTP folders); '
								 'read-only, nothing is imported or uploaded')
		parser.add_argument('--revoice-whole-verb', action='store_true', dest='revoice_whole_verb',
							help='When any form of a verb is voiced, voice all its other forms too (all tenses), '
								 'so a conjugation never mixes old and new audio')
		parser.add_argument('--revoice', action='store_true', dest='is_revoice',
							help='Voice new verbs/forms and those whose translation changed')
		parser.add_argument('--id', dest='ids', action='append', type=int, default=[],
							help='GRAND TABLE row ID whose form must be revoiced (repeatable)')

	def handle(self, *args, **options):
		# Table names and verbs are Cyrillic; a cp1252 console would crash on the first such line,
		# possibly in the middle of voicing, after the import has been saved
		for stream in (sys.stdout, sys.stderr):
			if hasattr(stream, 'reconfigure') and (stream.encoding or '').lower().replace('-', '') != 'utf8':
				stream.reconfigure(encoding='utf-8', errors='backslashreplace')
		if options['check_voice']:
			return self.check_voicing()
		self.verbosity = options['verbosity']
		self.only_differences = options['only_differences']
		self.revoice_whole_verb = options['revoice_whole_verb']
		self.report = defaultdict(list)
		self.summary = []
		table_dir = options['dir']
		small_rows = read_table(os.path.join(table_dir, SMALL_TABLE))
		grand_rows = read_table(os.path.join(table_dir, GRAND_TABLE), FORM_TABLE_COLUMNS)
		for path in chain.from_iterable(expand_paths(table_dir, pattern) for pattern in options['join']):
			rows = read_table(path, FORM_TABLE_COLUMNS)
			self.add_summary(f'Joined {len(rows)} rows from {os.path.basename(path)}')
			grand_rows += rows
		relation_rows = read_table(os.path.join(table_dir, RELATIONS_TABLE))

		with transaction.atomic():
			verbs, verbs_to_revoice = self.sync_verbs(small_rows, grand_rows)
			forms_to_revoice, form_tenses = self.sync_forms(
				grand_rows, relation_rows, verbs, set(options['ids']), options['prune'])
			self.sync_relations(relation_rows, verbs, form_tenses, options['prune'])
			if options['dry_run']:
				transaction.set_rollback(True)

		self.add_summary(f'To voice: {len(verbs_to_revoice)} verbs, {len(forms_to_revoice)} forms'
						 f'{" (listed in the report)" if options["report"] else " (use --report to list them)"}')
		for warning in chain.from_iterable(self.report[section] for section in WARNING_SECTIONS):
			self.stderr.write(self.style.WARNING(warning))
		if options['report']:
			self.write_report(options['report'], table_dir, options)

		if options['dry_run']:
			self.stdout.write(self.style.NOTICE('Dry run: all changes rolled back'))
			return

		if options['is_revoice']:
			for verb in verbs_to_revoice:
				self.log(f'Voicing verb {verb.pk}: {verb}')
				verb.to_voice(overwrite=True)
			for form in forms_to_revoice:
				self.log(f'Voicing form {form.pk}: {form}')
				form.to_voice(overwrite=True)
		elif verbs_to_revoice or forms_to_revoice:
			self.stdout.write(self.style.NOTICE(
				f'{len(verbs_to_revoice)} verbs and {len(forms_to_revoice)} forms need voicing; '
				f'rerun with --revoice or use dictionary_voice_verbs for missing audio'))

	def check_voicing(self):
		from le_francais_dictionary import tts

		failures = []

		def check(name, test):
			try:
				detail = test()
			except Exception as e:
				failures.append(name)
				self.stdout.write(self.style.ERROR(f'FAIL  {name}: {type(e).__name__}: {e}'))
			else:
				self.stdout.write(self.style.SUCCESS(f'OK    {name}') + (f': {detail}' if detail else ''))

		def env(*names):
			missing = [name for name in names if not os.environ.get(name)]
			if missing:
				raise ValueError(f'not set: {", ".join(missing)}')

		def credentials_file():
			path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
			if not path:
				raise ValueError('GOOGLE_APPLICATION_CREDENTIALS is not set')
			if not os.path.isfile(path):
				raise FileNotFoundError(path)
			return path

		def google_voices():
			from google.cloud import texttospeech
			client = texttospeech.TextToSpeechClient()
			# Voices used by Verb.to_voice / VerbForm.to_voice
			found = []
			for (language, _), name in sorted(tts.VERB_VOICES.items()):
				available = {voice.name for voice in client.list_voices(language_code=language).voices}
				if name not in available:
					raise ValueError(f'voice {name} is not available (change VERB_VOICES in tts.py)')
				found.append(name)
			return ', '.join(found)

		def sftp_folders():
			srv = tts.get_sftp_srv()
			try:
				for path in (tts.FTP_FR_VERBS_PATH, tts.FTP_RU_VERBS_PATH):
					if not srv.isdir(path):
						raise FileNotFoundError(f'{path} not found on the server')
			finally:
				srv.close()
			return f'{tts.FTP_FR_VERBS_PATH}, {tts.FTP_RU_VERBS_PATH}'

		check('SFTP settings', lambda: env('SFTP_FILES_LE_FRANCAIS_HOSTNAME', 'SFTP_FILES_LE_FRANCAIS_USERNAME',
										   'SFTP_FILES_LE_FRANCAIS_PASSWORD'))
		check('Google credentials file', credentials_file)
		check('Google TTS voices', google_voices)
		check('SFTP connection and folders', sftp_folders)

		if failures:
			raise CommandError(f'Voicing is not ready: {", ".join(failures)} failed')
		self.stdout.write(self.style.SUCCESS('Voicing is ready (file upload permissions are not tested)'))

	def log(self, message, level=2):
		if self.verbosity >= level:
			self.stdout.write(message)

	def add_summary(self, message):
		self.summary.append(message)
		self.stdout.write(message)

	def write_report(self, path, table_dir, options):
		mode = 'dry run, nothing saved' if options['dry_run'] else 'import'
		lines = [
			'Verbs for cards import report',
			f'Date: {timezone.localtime().strftime("%Y-%m-%d %H:%M")} ({mode})',
			f'Tables: {os.path.abspath(table_dir)}',
			'',
		] + self.summary
		for section in REPORT_SECTIONS:
			entries = self.report[section]
			lines += ['', f'{section}: {len(entries)}', '-' * len(section)]
			lines += entries or ['(none)']
		with open(path, 'w', encoding='utf-8') as f:
			f.write('\n'.join(lines) + '\n')
		self.stdout.write(f'Report written to {path}')

	def sync_verbs(self, small_rows, grand_rows):
		translations = {}
		for row in small_rows:
			infinitive = row['INFINITIVE'].strip()
			if infinitive:
				translations[infinitive] = (row['TRANSLATION'].strip(), row['RU_SYNT'].strip())

		attributes = OrderedDict()
		for row in grand_rows:
			infinitive = row['VERBE'].strip()
			if infinitive and infinitive not in attributes:
				attributes[infinitive] = (
					TYPE_AFFIRMATIVE if row['TYPE'].strip() == 'affirmative' else TYPE_NEGATIVE,
					row['CLASS'].strip() == 'regular',
				)

		verbs = {verb.verb: verb for verb in Verb.objects.all()}
		to_create, to_update, to_revoice = [], [], []
		for infinitive, (verb_type, regular) in attributes.items():
			translation = translations.get(infinitive)
			verb = verbs.get(infinitive)
			if verb is None:
				if translation is None:
					self.report[SKIPPED_INFINITIVES].append(infinitive)
					continue
				verb = Verb(verb=infinitive, type=verb_type, regular=regular)
				verb.translation, verb.translation_text = translation
				to_create.append(verb)
				self.report[TO_VOICE].append(f'verb {infinitive} -- new ("{translation[0]}" / "{translation[1]}")')
				continue
			changed = (verb.type, verb.regular) != (verb_type, regular)
			verb.type, verb.regular = verb_type, regular
			if translation is not None and (verb.translation, verb.translation_text) != translation:
				self.report[TO_VOICE].append(
					f'verb {infinitive} (id {verb.pk}) -- translation changed: '
					f'"{verb.translation}" / "{verb.translation_text}" -> "{translation[0]}" / "{translation[1]}"')
				verb.translation, verb.translation_text = translation
				changed = True
				to_revoice.append(verb)
			if changed:
				to_update.append(verb)

		for verb in to_create:
			self.log(f'New verb: {verb.verb}')
			verb.save()
			verbs[verb.verb] = verb
		for verb in to_update:
			self.log(f'Updated verb: {verb.verb}')
		bulk_update(to_update, update_fields=['type', 'regular', 'translation', 'translation_text'])

		self.add_summary(f'Verbs: {len(to_create)} created, {len(to_update)} updated')
		return verbs, to_create + to_revoice

	def sync_forms(self, grand_rows, relation_rows, verbs, revoice_ids, prune):
		# Forms belong to a verb and a tense, not to a lesson: the same form listed
		# under several lessons is imported once, at its first position.
		# A row without ID / LESSON_NO is still imported when RELATIONS places its verb and tense in a lesson.
		related = {(row['VERBE'].strip(), get_tense_id(row['TENSE'])) for row in relation_rows
				   if row['LESSON_NO'].strip() not in ('', '0')}
		rows = OrderedDict()
		forced = set()
		skipped = OrderedDict()
		duplicates = duplicates_with_differences = 0
		for row in grand_rows:
			infinitive = row['VERBE'].strip()
			tense = get_tense_id(row['TENSE'])
			reasons = [] if row['TRANSLATION'].strip() else ['no TRANSLATION']
			if (infinitive, tense) not in related:
				reasons += [f'no {column}' for column in ('ID', 'LESSON_NO') if not cell(row, column)]
				if cell(row, 'LESSON_NO') == '0':
					reasons.append('LESSON_NO is 0')
				if reasons and reasons != ['no TRANSLATION']:
					reasons.append('not in RELATIONS')
			if tense is None:
				reasons.append(f'unknown tense "{row["TENSE"]}"')
			if infinitive not in verbs:
				reasons.append('infinitive not in SMALL TABLE')
			if reasons:
				skipped.setdefault((row['_source'], infinitive, row['TENSE'].strip(), ', '.join(reasons)), []) \
					.append(row['_line'])
				continue
			key = (verbs[infinitive].pk, tense, row['CONJUGAISON'].strip())
			first = rows.setdefault(key, row)
			if first is not row:
				differences = [f'{column}: "{cell(first, column)}" vs "{cell(row, column)}"'
							   for column in DUPLICATE_COMPARED_COLUMNS if cell(first, column) != cell(row, column)]
				duplicates += 1
				duplicates_with_differences += bool(differences)
				if differences or not self.only_differences:
					self.report[DUPLICATE_FORMS].append(
						f'{infinitive} / {row["TENSE"].strip()} / {key[2]}: used {first["_source"]} line {first["_line"]}, '
						f'ignored {row["_source"]} line {row["_line"]} -- {"; ".join(differences) or "no difference"}')
			if cell(row, 'ID').isdigit() and int(cell(row, 'ID')) in revoice_ids:
				forced.add(key)
		for (source, infinitive, tense_name, reasons), lines in skipped.items():
			self.report[SKIPPED_GRAND_ROWS].append(
				f'{infinitive or "(no VERBE)"} / {tense_name or "(no TENSE)"}: '
				f'{len(lines)} rows, {source} lines {format_ranges(lines)} -- {reasons}')
		if duplicates:
			self.add_summary(f'Duplicate forms: {duplicates} listed more than once, '
							 f'{duplicates_with_differences} with differences (first one is used)')

		verb_names = {verb.pk: verb.verb for verb in verbs.values()}
		existing = {}
		existing_by_form = defaultdict(list)
		for form in VerbForm.objects.select_related('verb').order_by('pk'):
			existing.setdefault((form.verb_id, form.tense, form.form), form)
			existing_by_form[(form.verb_id, form.form)].append(form)
		claimed = set()

		order = Counter()
		to_create, to_update, to_revoice = [], [], []
		imported = []  # (form, label) for every form in the tables
		for key, row in rows.items():
			verb_id, tense, text = key
			order[(verb_id, tense)] += 1
			values = {
				'verb_id': verb_id,
				'tense': tense,
				'order': order[(verb_id, tense)],
				'is_shown': cell(row, 'IS_SHOWN') == '1',
				'form_to_show': get_form_to_show(text),
				'translation': row['TRANSLATION'].strip(),
				'translation_text': row['RU SYNTH'].strip(),
			}
			form = existing.get(key)
			if form is None or form.pk in claimed:
				# Reuse a form stored under another tense rather than recreating it with no audio
				form = next((f for f in existing_by_form[(verb_id, text)] if f.pk not in claimed), None)

			label = f'form {verb_names[verb_id]} / {row["TENSE"].strip()} / {text}'
			if form is None:
				form = VerbForm(form=text, **values)
				imported.append((form, label))
				to_create.append(form)
				to_revoice.append(form)
				self.report[TO_VOICE].append(
					f'{label} -- new ("{values["translation"]}" / "{values["translation_text"]}")')
				continue

			claimed.add(form.pk)
			imported.append((form, label))
			if any(getattr(form, field) != value for field, value in values.items()):
				if (form.translation, form.translation_text) != (values['translation'], values['translation_text']):
					to_revoice.append(form)
					self.report[TO_VOICE].append(
						f'{label} (id {form.pk}) -- translation changed: "{form.translation}" / '
						f'"{form.translation_text}" -> "{values["translation"]}" / "{values["translation_text"]}"')
				for field, value in values.items():
					setattr(form, field, value)
				to_update.append(form)
			if key in forced and form not in to_revoice:
				to_revoice.append(form)
				self.report[TO_VOICE].append(f'{label} (id {form.pk}) -- requested with --id')

		if self.revoice_whole_verb:
			changed_verbs = {form.verb_id for form in to_revoice}
			revoiced = {id(form) for form in to_revoice}
			for form, label in imported:
				if form.verb_id in changed_verbs and id(form) not in revoiced:
					to_revoice.append(form)
					self.report[TO_VOICE].append(f'{label} (id {form.pk}) -- another form of this verb is voiced')

		VerbForm.objects.bulk_create(to_create)
		bulk_update(to_update, update_fields=FORM_FIELDS, batch_size=200)
		for form in to_create:
			self.log(f'New form: {form}')

		stale = [form for form in chain.from_iterable(existing_by_form.values()) if form.pk not in claimed]
		self.add_summary(f'Forms: {len(to_create)} created, {len(to_update)} updated, '
						 f'{len(stale)} not in the forms tables')
		# Packets that currently show each stale form (relations are synced after forms)
		packets = defaultdict(list)
		relations = VerbPacketRelation.objects.filter(verb_id__in={form.verb_id for form in stale}) \
			.order_by('packet_id').values_list('verb_id', 'tense', 'packet__name')
		for verb_id, tense, packet_name in relations:
			packets[(verb_id, tense)].append(packet_name)

		def get_packets(form):
			return ', '.join(packets[(form.verb_id, form.tense)]) or 'none'

		def describe(form):
			return (f'{form.form} - {form.translation} | verb: {form.verb or "-"} | '
					f'tense: {form.get_tense_display() or "-"} | packets: {get_packets(form)}')

		stale_groups = OrderedDict()
		for form in stale:
			stale_groups.setdefault((str(form.verb or '-'), form.get_tense_display() or '-', get_packets(form)), []) \
				.append(form)
		for (verb_name, tense_name, packet_names), forms in stale_groups.items():
			self.report[STALE_FORMS].append(
				f'{verb_name} / {tense_name} -- packets: {packet_names} -- {len(forms)} forms '
				f'(ids {format_ranges(f.pk for f in forms)}): {"; ".join(f.form or "" for f in forms)}')

		self.delete_stale(VerbForm, stale, prune, 'forms', level=1, describe=describe)
		return to_revoice, {key[:2] for key in rows}

	def sync_relations(self, relation_rows, verbs, form_tenses, prune):
		lessons = {lesson.lesson_number: lesson for lesson in LessonPage.objects.all()}
		packets_by_lesson = {}
		packets_by_name = {}
		for packet in VerbPacket.objects.select_related('lesson').order_by('pk'):
			if packet.lesson is not None:
				packets_by_lesson.setdefault(packet.lesson.lesson_number, packet)
			packets_by_name.setdefault(packet.name, packet)

		def get_packet(code):
			if code.isdigit():
				lesson_number = int(code)
				if lesson_number not in lessons and 1000 < lesson_number < 2000:
					# 10xx rows are additions to lesson xx (e.g. 1029 is the participe passé of lesson 29)
					lesson_number -= 1000
				if lesson_number in packets_by_lesson:
					return packets_by_lesson[lesson_number]
				if lesson_number not in lessons:
					packets_by_lesson[lesson_number] = None
					return None
				name, lesson = f'Глаголы урока {lesson_number}', lessons[lesson_number]
			else:
				# Lectures without a lesson page (N01, CDF01, ...)
				name, lesson = f'Глаголы лекции {code}', None
				if name in packets_by_name:
					return packets_by_name[name]
			packet = VerbPacket.objects.create(name=name, lesson=lesson)
			self.log(f'New packet: {name}', level=1)
			if lesson is not None:
				packets_by_lesson[lesson.lesson_number] = packet
			packets_by_name[name] = packet
			return packet

		existing = {}
		stale = []
		duplicate_of = {}
		for relation in VerbPacketRelation.objects.select_related('packet', 'verb').order_by('pk'):
			key = (relation.packet_id, relation.verb_id, relation.tense)
			if key in existing:
				stale.append(relation)
				duplicate_of[relation.pk] = existing[key].pk
			else:
				existing[key] = relation

		# Rows are in the ORDER column's order; positions are renumbered per packet
		seen = set()
		order = Counter()
		to_create, to_update = [], []
		for line, row in enumerate(relation_rows, start=2):
			code = row['LESSON_NO'].strip()
			infinitive = row['VERBE'].strip()
			tense = get_tense_id(row['TENSE'])
			label = f'line {line}: {infinitive} / {row["TENSE"].strip()} / lesson {code or "-"}'
			if code in ('', '0'):
				self.report[SKIPPED_RELATIONS].append(f'{label} -- no LESSON_NO' if not code else f'{label} -- LESSON_NO is 0')
				continue
			if tense is None:
				self.report[SKIPPED_RELATIONS].append(f'{label} -- unknown tense')
				continue
			verb = verbs.get(infinitive)
			if verb is None:
				self.report[SKIPPED_RELATIONS].append(f'{label} -- infinitive not found')
				continue
			packet = get_packet(code)
			if packet is None:
				self.report[SKIPPED_RELATIONS].append(f'{label} -- lesson does not exist')
				continue
			key = (packet.pk, verb.pk, tense)
			if key in seen:
				self.report[SKIPPED_RELATIONS].append(f'{label} -- duplicate row')
				continue
			seen.add(key)
			order[packet.pk] += 1
			if (verb.pk, tense) not in form_tenses:
				self.report[RELATIONS_WITHOUT_FORMS].append(f'{label} ({packet})')

			relation = existing.pop(key, None)
			if relation is None:
				to_create.append(VerbPacketRelation(packet=packet, verb=verb, tense=tense, order=order[packet.pk]))
			elif relation.order != order[packet.pk]:
				relation.order = order[packet.pk]
				to_update.append(relation)

		VerbPacketRelation.objects.bulk_create(to_create)
		bulk_update(to_update, update_fields=['order'])
		stale.extend(existing.values())
		self.add_summary(f'Relations: {len(to_create)} created, {len(to_update)} reordered, '
						 f'{len(stale) - len(duplicate_of)} not in RELATIONS, {len(duplicate_of)} duplicates')

		def describe(relation):
			reason = (f'duplicate of id {duplicate_of[relation.pk]}' if relation.pk in duplicate_of
					  else 'not in RELATIONS')
			return f'{relation.packet} / {relation.verb} / {relation.get_tense_display()} -- {reason}'

		self.report[STALE_RELATIONS] += [f'{describe(r)} (id {r.pk})' for r in stale]
		self.delete_stale(VerbPacketRelation, stale, prune, 'relations', level=1, describe=describe)

	def delete_stale(self, model, objects, prune, label, level=2, describe=str):
		if not objects:
			return
		for obj in objects:
			self.log(f'  stale {model.__name__} {obj.pk}: {describe(obj)}', level=level)
		if prune:
			model.objects.filter(pk__in=[obj.pk for obj in objects]).delete()
			self.add_summary(f'Deleted {len(objects)} stale {label}')
		else:
			self.add_summary(f'Kept {len(objects)} stale {label} (use --prune to delete)')
