from datetime import datetime

from django import forms
from django.db.models import Q, F, Case, When
from typing import List

from le_francais_dictionary.models import Packet, UserWordRepetition, \
	Word, \
	UserWordData, UserWordIgnore, WordTranslation, WordGroup, \
	prefetch_words_data, get_repetition_words_query, VerbPacket, Verb, \
	VerbPacketRelation

from .sm2 import sm2_ef_q_mq


class DictionaryCsvImportForm(forms.Form):
	csv_file = forms.FileField()


from operator import attrgetter, methodcaller


def value(p_value, o):
	return p_value(o) if callable(p_value) else p_value


def row(name, o, p_value, p_sort_value=None, p_filter_value=None):
	result = dict()
	result['value'] = value(p_value, o)
	if p_sort_value:
		result['sort-value'] = value(p_sort_value, o)
	if p_filter_value:
		result['filter-value'] = value(p_filter_value, o)
	return {name: result}


class WordsManagementFilterForm(forms.Form):

	def __init__(self, user, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user=user
		if self.user.is_authenticated and not self.user.must_pay:
			self.packets = Packet.objects.all()
		elif self.user.is_authenticated and self.user.has_lessons:
			self.packets = Packet.objects.filter(Q(demo=True) | Q(
				lesson__payment__user=user)).distinct()
		elif self.user.is_authenticated:
			self.packets = Packet.objects.filter(Q(demo=True) | Q(
					lesson__payment__user=user)).distinct()
		else:
			self.packets = Packet.objects.filter(demo=True).distinct()
		choices = [(o.id, str(o.name)) for o in self.packets]
		# TODO: has_repetition_words method
		if self.user.is_authenticated and get_repetition_words_query(self.user, filter_excluded=False).count() > 0:
			choices = [(88888888, 'Слова на повторение')] + choices
		self.fields['packets'] = forms.MultipleChoiceField(choices=choices)
		# name, title, type, visible, sortable, filterable, p_filter_value, p_sort_value, p_value
		self.COLUMNS_ATTRS = [
			'name', 'title', 'type', 'visible', 'sortable', 'filterable',
		]
		self.COLUMNS = [
			# ('_checkbox', "<input type='checkbox'>",'text',  True, False, False, None, None, '<input type="checkbox">'),
			('id', 'ID', None, False, False, False, None, None, attrgetter('pk')),
			('deleted', 'Удалено', None, False, False, False, methodcaller('is_marked', self.user), None, methodcaller('is_marked', self.user)),
			('word', 'Слово', attrgetter('html_class'), True, True, True, None, None, attrgetter('table_html')),
			('translation', 'Перевод', attrgetter('html_class'), True, True, True,  None, None, attrgetter('first_translation.table_html')),
			('repetitions', '<i class="lamp-icon" title="На сколько вы продвинулись в запоминании слова"></i>', None, True, True, True, methodcaller('repetitions_count', self.user), None, methodcaller('repetitions_count', self.user)),
			('stars', 'Оценка <button class="btn funnel-filter-button" id="starsFilterContainer"></button>', 'cell-stars', True, True, True,  methodcaller('mean_quality_filter_value', self.user), methodcaller('mean_quality_filter_value', self.user), methodcaller('mean_quality', self.user)),
		]

	def set_words_cash(
			self,
			words:List[Word],
			user_data:List[UserWordData],

	):
		return

	def table_dict(self):
		if self.is_valid():
			data = self.cleaned_data
			if '88888888' in data['packets']:
				packets_list: List[int] = data['packets']
				packets_list.pop(packets_list.index('88888888'))
				query = Word.objects.filter(
					packet_id__in=packets_list
				)
				repetition_words = list(get_repetition_words_query(self.user, filter_excluded=False))
				packet_words = list(query)
				words = repetition_words + packet_words
				words = list(dict.fromkeys(words))
			else:
				query = Word.objects.filter(packet_id__in=data['packets'])
				words = list(query.distinct().order_by('order'))
			# time = datetime.now()
			words = prefetch_words_data(words, self.user)
			result = dict(
				columns=[dict(
					id=column[0],
					title=column[1],
					visible=column[3]
				) for column in self.COLUMNS],
				rows=[dict(
					id=word.pk,
					ru_audio_src=word.first_translation.polly_url,
					fr_audio_src=word.polly_url,
					cells=[dict(
						id=column[0],
						value=column[-1] if not callable(column[-1]) else column[-1](word),
						filter_value=column[-3] if not callable(column[-3]) else column[-3](word),
						visible=column[3],
						cls=column[2] if not callable(column[2]) else column[2](word),
					) for column in self.COLUMNS]
				) for word in words],
				empty='Выберите уроки (можно одновременно выбирать несколько) и нажмите на кнопку «Получить список слов».',
				empty_body='',
			)
			# print('Result:\t', datetime.now() - time)
			return result
		else:
			return dict(
				columns=[dict(
					id=column[0],
					title=column[1],
					visible=column[3]
				) for column in self.COLUMNS],
				rows=[],
				empty_header= '''Выберите уроки (можно одновременно выбирать
				              несколько) и нажмите на кнопку «Получить список
				              слов».''',
				empty_body='''<p>После получения списка вы можете делать
					выборку слов для изучения в соответствии с их оценкой
					(оценка отражает то, насколько успешно вы вспоминали
				    слово при самопроверках). Имеет смысл выбирать слова
				    с низким оценками.</p>
				    <p>Не делайте слишком большую выборку. Проигрывание очень
				    длинного списка слов теряет практический смысл,
				    кроме того, загрузка его в словарь для произношения
				    займёт заметное время.</p>
				    <p>Мы рекомендуем ограничиваться примерно ста 
				    пятьдесятью словами — больше не желательно.</p>
				    <div class="alert alert-success">
				    <p>P.S. Перечень загруженных слов, фильтры и список
				    отмеченных слов сохраняются на лету — вы сможете спокойно
				    уйти с этой страницы и при следующем заходе восстановить ее состояние одним нажатием кнопки «Повторить последнюю выборку».</p></div>''',
			)


class DictionaryWordForm(forms.Form):
	cd_id = forms.IntegerField()
	word = forms.CharField()
	translation = forms.CharField()
	genre = forms.CharField(required=False)
	plural = forms.BooleanField(required=False)
	part_of_speech = forms.CharField(required=False)
	packet = forms.CharField()


DictionaryWordFormset = forms.formset_factory(DictionaryWordForm)

def get_tense_display_value(values):
	v = values['verbpacketrelation__tense']
	return dict(
		VerbPacketRelation._meta.get_field('tense').flatchoices
	).get(v, v)

def get_regular_display_value(values):
	v = values['regular']
	if v:
		return 'Regular'
	return 'Irregular'

def get_regular_filter_value(values):
	v = values['regular']
	return v

def get_type_display_value(values):
	v = values['type']
	return dict(
		Verb._meta.get_field('type').flatchoices
	).get(v, v)

def get_type_filter_value(values):
	return values['type']

class VerbsManagementFilterForm(forms.Form):

	def __init__(self, user, *args, **kwargs):
		super(VerbsManagementFilterForm, self).__init__(*args, **kwargs)
		self.user = user
		self.packets = VerbPacket.objects.all().order_by('lesson__lesson_number')
		if user.must_pay:
			self.packets = self.packets.filter(Q(lesson__users=user) | Q(lesson__lesson_number__lte=11)).distinct()
		packet_choices = [(o.id, o.name) for o in self.packets]
		self.fields['packets'] = forms.MultipleChoiceField(choices=packet_choices)
		self.COLUMNS = [
			('id', 'ID', None, False, False, False, None, None, methodcaller('get', 'verbpacketrelation__pk')),
			('type', 'TYPE', None, False, False, False, get_type_filter_value, None, get_type_display_value),
			('regular', 'Правильный/Неправильный', None, False, False, False, get_regular_filter_value, None, get_regular_display_value),
			('verb', 'Глагол', None, True, True, True, None, None, methodcaller('get', 'verb')),
			('tense', 'Время', None, True, True, True, None, None, get_tense_display_value),
			('translation', 'Перевод', None, True, True, True, None, None, methodcaller('get', 'translation')),
		]


	def table_dict(self):
		if self.is_valid():
			data = self.cleaned_data
			verbs_list = Verb.objects.annotate().filter(packets__in=data['packets']).values(
				'verbpacketrelation__tense', 'verbpacketrelation__pk',
				'verb', 'translation',
				'polly',
				'audio_url',
				'translation_polly',
				'translation_audio_url',
				'type',
				'regular'
				).order_by('verbpacketrelation__order')
			result = dict(
				columns=[dict(
					id=column[0],
					title=column[1],
					visible=column[3]
				) for column in self.COLUMNS],
				rows=[dict(
					id=verb['verbpacketrelation__pk'],
					ru_audio_src=verb['translation_audio_url'],
					fr_audio_src=verb['audio_url'],
					cells=[dict(
						id=column[0],
						value=column[-1] if not callable(
							column[-1]) else column[-1](verb),
						filter_value=column[-3] if not callable(
							column[-3]) else column[-3](verb),
						visible=column[3],
						cls=column[2] if not callable(column[2]) else column[2](verb),
					) for column in self.COLUMNS]
				) for verb in verbs_list],
				empty='',
				empty_body='',
			)
		else:
			result = dict(
				columns=[dict(
					id=column[0],
					title=column[1],
					visible=column[3]
				) for column in self.COLUMNS],
				rows=[],
				empty_header='''Выберите уроки (можно одновременно выбирать
							              несколько) и нажмите на кнопку «Получить список
							              глаголов».''',
				empty_body='''''',
			)
		return result
