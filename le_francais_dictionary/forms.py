from django import forms
from django.db.models import Q

from le_francais_dictionary.models import Packet, UserPacket, Word


class DictionaryCsvImportForm(forms.Form):
	csv_file = forms.FileField()


class WordsManagementFilterForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super().__init__(*args, **kwargs)
		packets = Packet.objects.filter(Q(demo=True)|Q(lesson__payment__user=user)).distinct().order_by('lesson__lesson_number', 'name')
		self.user=user
		self.fields['packets'] = forms.MultipleChoiceField(choices=[(o.id, str(o.name)) for o in packets])
		self.fields['show_only_learned'] = forms.BooleanField(label='Только выученные', required=False, initial=True)
		self.fields['show_deleted'] = forms.BooleanField(label='Показывать удаленные', required=False, initial=False)

	def footable_words(self):
		if self.is_valid():
			data = self.cleaned_data
			query = Word.objects.prefetch_related('userwordrepetition_set', 'userdata', 'userwordignore_set', 'wordtranslation_set').filter(packet_id__in=data['packets'])
			if data['show_only_learned']:
				query.filter(userdata__user=self.user)
			if not data['show_deleted']:
				query.exclude(userwordignore__user=self.user)
			return dict(
				columns=[
					{"name": "_selection", "title": "Selection",
					 'visible': False, "sortable": False, "filterable": False},
					{"name": "_checkbox",
					 "title": "<input type='checkbox' class='global-checkbox'>",
					 'visible': True, "sortable": False, "filterable": False},
					{'name': 'id', 'visible': False},
					{'name': 'word', 'title': 'Слово'},
					{'name': 'translation', 'title': 'Перевод'}
				],
				rows=[
					{'id': word.pk, '_checkbox': '<input type="checkbox" class="row-checkbox">', 'word': str(word),
					 'translation': str(word.first_translation)} for word in
					list(query)
				],
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
