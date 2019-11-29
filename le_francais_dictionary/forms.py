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
		# name, title, visible, sortable, filterable, p_filter_value, p_sort_value, p_value
		self.COLUMNS_ATTRS = [
			'name', 'title', 'visible', 'sortable', 'filterable',
		]
		self.COLUMNS = [
			('_checkbox', "<input type='checkbox'>", True, False, False, None, None, '<input type="checkbox">'),
			('id', 'ID', False, False, False, None, None, attrgetter('pk')),
			('deleted', 'Удалено', False, False, False, None, None, methodcaller('is_marked', self.user)),
			('word', 'Слово', True, True, True, None, None, attrgetter('word')),
			('translation', 'Перевод', True, True, True,  None, None, attrgetter('first_translation.translation')),
			('repetitions', 'Повторений', True, True, True, methodcaller('repetitions_count', self.user), None, methodcaller('repetitions_count', self.user)),
			('difficulty', 'Оценка', True, True, True,  methodcaller('mean_quality', self.user), None, methodcaller('mean_quality', self.user))
		]


	def footable_words(self):
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
				columns=[
					{key: col[i] for (i, key) in enumerate(self.COLUMNS_ATTRS)
					 if col[i] != None} for col in self.COLUMNS],
				rows=[{(col[0]): dict(
					value=(col[-1] if isinstance(col[-1], str) else col[-1](word)),
					options=(dict(
						filterValue=col[-3] if isinstance(col[-3], str) else col[-3](word))
				if col[-3] else dict() )) for col in self.COLUMNS} for word in list(query)],
			)
		else:
			return None


class DictionaryWordForm(forms.Form):
	cd_id = forms.IntegerField()
	word = forms.CharField()
	translation = forms.CharField()
	genre = forms.CharField(required=False)
	plural = forms.BooleanField(required=False)
	part_of_speech = forms.CharField(required=False)
	packet = forms.CharField()


DictionaryWordFormset = forms.formset_factory(DictionaryWordForm)
