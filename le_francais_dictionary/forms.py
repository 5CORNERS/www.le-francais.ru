from datetime import datetime

from django import forms
from django.db.models import Q
from typing import List

from le_francais_dictionary.models import Packet, UserWordRepetition, Word, \
	UserWordData, UserWordIgnore, WordTranslation, WordGroup, \
	prefetch_words_data

from .utils import sm2_ef_q_mq


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
		if not self.user.must_pay:
			self.packets = Packet.objects.all().order_by(
				'lesson__lesson_number', 'name')
		elif self.user.has_lessons:
			self.packets = Packet.objects.filter(Q(demo=True) | Q(
				lesson__payment__user=user)).distinct().order_by(
				'lesson__lesson_number', 'name')
		else:
			self.packets = Packet.objects.filter(
				Q(word__userdata__user=user) | Q(
					lesson__payment__user=user)).distinct().order_by(
				'lesson__lesson_number', 'name')
		self.fields['packets'] = forms.MultipleChoiceField(choices=[(o.id, str(o.name)) for o in self.packets])
		# name, title, type, visible, sortable, filterable, p_filter_value, p_sort_value, p_value
		self.COLUMNS_ATTRS = [
			'name', 'title', 'type', 'visible', 'sortable', 'filterable',
		]
		self.COLUMNS = [
			# ('_checkbox', "<input type='checkbox'>",'text',  True, False, False, None, None, '<input type="checkbox">'),
			('id', 'ID', None, False, False, False, None, None, attrgetter('pk')),
			('deleted', 'Удалено', None, False, False, False, methodcaller('is_marked', self.user), None, methodcaller('is_marked', self.user)),
			('word', 'Слово', None, True, True, True, None, None, attrgetter('word')),
			('translation', 'Перевод', None, True, True, True,  None, None, attrgetter('first_translation.translation')),
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
			query = Word.objects.prefetch_related(
				'userwordrepetition_set', 'userdata', 'userwordignore_set',
				'wordtranslation_set', 'group'
			).filter(packet_id__in=data['packets'])
			# time = datetime.now()
			words = list(query.distinct().order_by('order'))
			words = prefetch_words_data(words, self.user)
			result = dict(
				columns=[dict(
					id=column[0],
					title=column[1],
					visible=column[3]
				) for column in self.COLUMNS],
				rows=[dict(
					id=word.pk,
					cells=[dict(
						id=column[0],
						value=column[-1] if not callable(column[-1]) else column[-1](word),
						filter_value=column[-3] if not callable(column[-3]) else column[-3](word),
						visible=column[3],
						cls=column[2],
					) for column in self.COLUMNS]
				) for word in words],
				empty='Выберите уроки (можно одновременно выбирать несколько) и нажмите на кнопку «Получить список слов». Или восстановите предыдущий выбор (если он был) соответствующей кнопкой.',
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
				empty_header= 'Выберите уроки (можно одновременно выбирать несколько) '
				              'и нажмите на кнопку «Получить список слов».',
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
				    пятьдесятью словами — больше не желательно.</p>''',
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
