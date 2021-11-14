from django import forms


class GetStatisticsForm(forms.Form):
    date_start = forms.DateField(label='start')
    date_end = forms.DateField(label='end')
