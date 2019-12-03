from django import forms
from django.db.models import Q

from le_francais_dictionary.models import Packet, UserPacket, Word


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
		self.fields['show_deleted'] = forms.BooleanField(label='Показывать удаленные', required=False, initial=False)
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
			query = query.distinct().order_by('order')
			return dict(
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
				) for word in list(query)],
				empty='Мои слова',
			)
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
