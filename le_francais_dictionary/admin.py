import csv
import re
from io import TextIOWrapper
from typing import List, Dict

from django.conf.urls import url
from django.contrib import admin
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from home.models import LessonPage
from .forms import DictionaryCsvImportForm, DictionaryWordFormset
from .models import Word, WordTranslation, Packet, WordPacket, WordGroup, \
	UnifiedWord

from django_bulk_update import helper as update_helper
import time

def get_number(s) -> int:
	m = re.match(r'\d+', s)
	if m:
		return int(m.group(0))


def create_polly_task(modeladmin: admin.ModelAdmin, request, qs):
	for p in qs:
		p.create_polly_task()


class WordTranslationInline(admin.TabularInline):
	model = WordTranslation
	readonly_fields = ['polly']
	extra = 1


class WordInline(admin.StackedInline):
	model = WordPacket
	fields = ['word']
	readonly_fields = ['word']
	extra = 1


class ImportTableRow:
	def __init__(
			self, i, packet_n, word, unified_word, translation,
			unified_translation, definition_num=None, cd_id=None,
			part_of_speech=None, genre=None, ru_voice=None, fr_voice=None,
			ru_voice_unified=None, fr_voice_unified=None,
			order=None):
		"""
		:type i: int
		:type packet_n: str
		:type word: str
		:type translation: str
		"""
		self.i = i
		self.cd_id = int(cd_id)
		self._packet = packet_n
		self.lesson_number = get_number(self._packet)
		self.packet_name = 'урок ' + self._packet
		self.unified_word = unified_word
		self.word = word
		self.translation = translation
		self.unified_translation = unified_translation
		self.definition_num = int(definition_num) if definition_num else None
		self.locution = True if 'loc' in part_of_speech else False
		self._genre = genre
		self.genre = genre.split(',')[0].strip() if genre else None
		self.plural = True if genre.split(
			',')[-1].strip() == 'pl' else False
		grammatical_number = genre.split(',')[-1].strip()
		from le_francais_dictionary.consts import GRAMMATICAL_NUMBER_LIST
		if grammatical_number in GRAMMATICAL_NUMBER_LIST:
			self.grammatical_number = genre.split(',')[-1].strip()
		else:
			self.grammatical_number = None
		if self.locution:
			self.part_of_speech = 'loc'
		else:
			self.part_of_speech = part_of_speech.split(' ')[0]
		self.ru_voice = ru_voice
		self.fr_voice = fr_voice
		self.ru_voice_unified = ru_voice_unified
		self.fr_voice_unified = fr_voice_unified
		self.order = order


class ImportTable:
	def __init__(self, rows: List[ImportTableRow]):
		self.rows = []
		for row in rows:
			self.rows.append(row)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
	change_list_template = 'dictionary/admin/change_list.html'
	list_display = ['cd_id', 'word', 'genre', 'part_of_speech', 'plural']
	ordering = ['cd_id']
	list_filter = ['genre', 'part_of_speech', 'plural']
	list_select_related = []
	readonly_fields = ['polly']
	inlines = [WordTranslationInline]
	actions = [create_polly_task]

	def get_urls(self):
		urls = super(WordAdmin, self).get_urls()
		my_urls = [
			url(
				'^import_csv/$',
				self.admin_site.admin_view(self.import_csv_view)
			),
			url(
				'^import_csv/update/$',
				self.admin_site.admin_view(self.update_csv_view)
			),
		]
		return my_urls + urls

	def error_redirect(self, request, message, level=messages.ERROR):
		self.message_user(request, message, level=level)
		return redirect('admin:le_francais_dictionary_word_changelist')


	def import_csv_view(self, request):
		if request.method == 'POST':
			start_time = time.time()
			form = DictionaryCsvImportForm(request.POST, request.FILES)
			if not form.is_valid():
				self.message_user(request, 'Form is not valid')
				return redirect('admin:le_francais_dictionary_word_changelist')
			csv_file = TextIOWrapper(
				request.FILES['csv_file'].file,
				encoding='utf-8',
				errors='replace'
			)

			rows: List[ImportTableRow] = []
			for i, row in enumerate(csv.reader(csv_file), 1):
				if i == 1:
					continue
				if row[1] and row[2] and row[10]:
					rows.append(
						ImportTableRow(
							i=i,
							packet_n=row[2],
							word=row[5],
							unified_word=row[3],
							translation=row[10],
							unified_translation=row[8],
							cd_id=row[1],
							part_of_speech=row[11],
							genre=row[12],
							order=row[0],
							definition_num=row[7]
						)
					)
			print("--- %s seconds --- Finished Reading" % (time.time() - start_time))
			import_table = ImportTable(rows)
			lesson_numbers_to_id = dict(LessonPage.objects.all().values_list(
				'lesson_number', 'id'
			))
			packets = list(Packet.objects.all())
			groups: List[WordGroup] = list(WordGroup.objects.prefetch_related('word_set', 'unifiedword_set').all())
			unified_words: List[UnifiedWord] = list(UnifiedWord.objects.all())
			words: List[Word] = list(Word.objects.prefetch_related('wordtranslation_set').all())
			WordTranslation.objects.all().delete()
			translations: List[WordTranslation] = []
			WordPacket.objects.all().delete()
			word_packets: List[WordPacket] = []
			for row in import_table.rows:

				# Packets getting or creating
				packet = next((p for p in packets if p.name == row.packet_name), None)
				if packet is None:
					packet = Packet(
						name=row.packet_name,
						lesson_id=lesson_numbers_to_id[row.lesson_number]
					)
					try:
						packet.clean_fields(exclude=['lesson'])
					except ValidationError as e:
						self.message_user(
							request,
							'Error in row {row.i}: {e}'.format(row=row, e=e),
							level=messages.ERROR,
						)
						return redirect(
							'admin:le_francais_dictionary_word_changelist')
					packet.save()
					packets.append(packet)

				# Groups with unified words creation and updating
				if row.definition_num:
					index, unified_word = next(
						((index_uw[0], index_uw[1]) for index_uw in
						 enumerate(unified_words) if
						 index_uw[1].word == row.unified_word and
						 index_uw[1].translation == row.unified_translation),
						(None, None))
					if unified_word is None:
						group = WordGroup.objects.create()
						unified_word = UnifiedWord(
							word=row.unified_word,
							translation=row.unified_translation,
							group=group,
							definition_num=row.definition_num
						)
						unified_words.append(unified_word)
					else:
						group = unified_word.group
						unified_word.word = row.unified_word
						unified_word.translation = row.unified_translation
						unified_word.definition_num = row.definition_num
						unified_words[index] = unified_word
				else:
					group = None

				start_time = time.time()
				word, index = next(((iw[1], iw[0]) for iw in enumerate(words) if iw[1].cd_id == row.cd_id), (None, None))
				if word is None:
					word = Word(
						cd_id=row.cd_id,
						packet=packet  # obsolete
					)
				word.word = row.word
				word.genre = row.genre
				word.plural = row.plural  # obsolete
				word.grammatical_number = row.grammatical_number
				word.part_of_speech = row.part_of_speech
				word.definition_num = row.definition_num
				word.group = group
				if index:
					words[index] = word
				else:
					words.append(word)
				try:
					word.clean_fields(exclude=['packet', 'group'])
				except ValidationError as e:
					self.message_user(
						request,
						'Error in row {row.i}: {e}'.format(row=row, e=e),
						level=messages.ERROR,
					)
					return redirect(
						'admin:le_francais_dictionary_word_changelist')
				word_packet = WordPacket(
					word_id=word.cd_id,
					packet_id=packet.id,
					order=row.order,
				)
				word_packets.append(
					word_packet
				)
				translation = next((t for t in translations if t.word_id == word.cd_id), None)
				if translation is None:
					translation = WordTranslation(
						word_id=word.cd_id,
						translation=row.translation,
						packet=packet
					)
					try:
						translation.clean_fields(exclude=['word', 'packet'])
					except ValidationError as e:
						self.message_user(
							request,
							'Error in row {row.i}: {e}'.format(row=row, e=e),
							level=messages.ERROR,
						)
						return redirect(
							'admin:le_francais_dictionary_word_changelist')
					translations.append(translation)
				print("--- %s seconds --- Word {w.word}".format(w=word) % (
							time.time() - start_time))
			update_helper.bulk_update(
				[w for w in words if not w._state.adding],
			)
			Word.objects.bulk_create(
				[w for w in words if w._state.adding]
			)
			update_helper.bulk_update(
				[uw for uw in unified_words if uw._state.adding]
			)
			UnifiedWord.objects.bulk_create(
				[uw for uw in unified_words if not uw._state.adding]
			)
			WordTranslation.objects.bulk_create(translations)
			WordPacket.objects.bulk_create(word_packets)
			self.message_user(request, 'CSV file has been imported')
			return redirect('admin:le_francais_dictionary_word_changelist')
		form = DictionaryCsvImportForm()
		context = dict(
			self.admin_site.each_context(request),
			form=form,
		)
		return render(
			request, 'dictionary/admin/csv_form.html', context
		)

	def update_csv_view(self, request, initial=None):
		if initial:
			form = DictionaryWordFormset(initial=[
				dict(
					cd_id=word.cd_id, word=word.word,
					translation=word.tra

				) for word in initial
			])


@admin.register(Packet)
class PacketAdmin(admin.ModelAdmin):
	list_display = ['name', 'lesson', 'demo', '_fully_voiced']
	ordering = ['lesson__lesson_number', 'name']
	actions = [create_polly_task]
	inlines = [WordInline]
