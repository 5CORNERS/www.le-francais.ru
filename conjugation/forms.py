# -*- coding: utf-8 -*-
from dal import autocomplete
from django import forms

from . import models


class BaseVerbTranslationForm(forms.ModelForm):
	"""Formset for editing phrases, which belong to verb"""
	fr_verb = forms.ModelChoiceField(queryset=models.Translation.objects.all(), widget=forms.HiddenInput())
	type = forms.CharField(widget=forms.HiddenInput(), initial='none')

	class Meta:
		model = models.Translation
		fields = ('fr_verb', 'ru_word', 'ru_tags', 'comment', 'order')
		widgets = {
			'ru_tags': autocomplete.ModelSelect2Multiple(url='conjugation:autocomplete_t_tag'),
			'order': forms.HiddenInput()
		}
		labels = {
			'ru_tags': 'Поисковые тэги',
			'comment': 'Комментарий'
		}


class VerbMainForm(BaseVerbTranslationForm):
	type = forms.CharField(widget=forms.HiddenInput(), initial='verb_translation')

	class Meta(BaseVerbTranslationForm.Meta):
		labels = {**BaseVerbTranslationForm.Meta.labels, **{
			'ru_word': 'Значение',
		}}


class VerbExampleForm(BaseVerbTranslationForm):
	type = forms.CharField(widget=forms.HiddenInput(), initial='example')

	class Meta(BaseVerbTranslationForm.Meta):
		fields = ('fr_word',) + BaseVerbTranslationForm.Meta.fields
		labels = {**BaseVerbTranslationForm.Meta.labels, **{
			'fr_word': 'Пример',
			'ru_word': 'Перевод примера',
		}}


class VerbCollocationForm(BaseVerbTranslationForm):
	type = forms.CharField(widget=forms.HiddenInput(), initial='collocation')

	class Meta(BaseVerbTranslationForm.Meta):
		fields = ('fr_word',) + BaseVerbTranslationForm.Meta.fields
		labels = {**BaseVerbTranslationForm.Meta.labels, **{
			'fr_word': 'Устойчивое выражение',
			'ru_word': 'Перевод уст. выражения',
		}}


class VerbIdiomForm(BaseVerbTranslationForm):
	type = forms.CharField(widget=forms.HiddenInput(), initial='idiom')

	class Meta(BaseVerbTranslationForm.Meta):
		fields = ('fr_word',) + BaseVerbTranslationForm.Meta.fields
		labels = {**BaseVerbTranslationForm.Meta.labels, **{
			'fr_word': 'Идиоматическое выражение',
			'ru_word': 'Перевод идиом. выражения',
		}}


forms_classes = [VerbMainForm, VerbExampleForm, VerbCollocationForm, VerbIdiomForm]
formsets = [forms.modelformset_factory(models.Translation, form=form) for form in forms_classes]
