from datetime import datetime

from django import forms
from django.db.models import Q
from typing import List

from le_francais_dictionary.models import Packet, UserWordRepetition, Word, UserWordData, UserWordIgnore, WordTranslation

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
		packets = Packet.objects.filter(Q(demo=True)|Q(lesson__payment__user=user)).distinct().order_by('lesson__lesson_number', 'name')
		self.user=user
		self.fields['packets'] = forms.MultipleChoiceField(choices=[(o.id, str(o.name)) for o in packets])
		self.fields['show_only_learned'] = forms.BooleanField(label='Только выученные', required=False, initial=True)
		self.fields['show_deleted'] = forms.BooleanField(label='Показывать исключенные', required=False, initial=False)
		# name, title, type, visible, sortable, filterable, p_filter_value, p_sort_value, p_value
		self.COLUMNS_ATTRS = [
			'name', 'title', 'type', 'visible', 'sortable', 'filterable',
		]
		self.COLUMNS = [
			# ('_checkbox', "<input type='checkbox'>",'text',  True, False, False, None, None, '<input type="checkbox">'),
			('id', 'ID', None, False, False, False, None, None, attrgetter('pk')),
			('deleted', 'Удалено', None, False, False, False, None, None, methodcaller('is_marked', self.user)),
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
				'wordtranslation_set',
			).filter(packet_id__in=data['packets'])
			if data['show_only_learned']:
				query = query.filter(userdata__user=self.user, userdata__grade=1)
			if not data['show_deleted']:
				query = query.exclude(userwordignore__user=self.user)
			# time = datetime.now()
			words = list(query.distinct().order_by('order'))
			translations = list(WordTranslation.objects.filter(word__in = words))
			ignored = list(UserWordIgnore.objects.filter(user=self.user, word__in=words))
			user_data = list(UserWordData.objects.filter(user=self.user, word__in=words).order_by('-datetime'))
			user_repetitions = list(UserWordRepetition.objects.filter(user=self.user, word__in=words))
			# print('Query:\t', datetime.now() - time)
			# time = datetime.now()
			for word in words:
				word_user_data = [ud for ud in user_data if ud.word_id == word.pk]
				if word_user_data:
					last_word_user_data = word_user_data[0]
					last_word_user_data._user_word_dataset = word_user_data
					word._last_user_data[self.user.pk] = last_word_user_data
				else:
					word._last_user_data[self.user.pk] = None
				if word.pk in [i.word_id for i in ignored]:
					word._is_marked[self.user.pk] = True
				else:
					word._is_marked[self.user.pk] = False
				user_word_repetitions = [uwr for uwr in user_repetitions if uwr.word_id == word.pk]
				if user_word_repetitions:
					word._repetitions_count[self.user.pk] = user_word_repetitions[0].time
				else:
					word._repetitions_count[self.user.pk] = None
				word_translations = [wt for wt in translations if wt.word_id == word.pk]
				if word_translations:
					word._first_translation = word_translations[0]
				else:
					word._first_translation = None
			# print('Caching:\t',datetime.now() - time)
			# time = datetime.now()
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
				empty='Мои слова',
			)
			# print('Result:\t', datetime.now() - time)
			return result
		else:
			return dict(
				columns_dicts=[dict(
					id=column[0],
					title=column[1],
					visible=column[2]
				) for column in self.COLUMNS],
				rows=[],
				empty= 'Мои слова',
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
