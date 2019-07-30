from django import forms


class DictionaryCsvImportForm(forms.Form):
	csv_file = forms.FileField()
	test = forms.BooleanField()
