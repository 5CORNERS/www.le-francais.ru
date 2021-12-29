from django import forms

from donations.models import DONATION_TARGET_ADS, DONATION_TARGET_LIFE


class SupportForm(forms.Form):
    type = forms.ChoiceField(
        choices=(
            ('recurrent', 'Каждый месяц'),
            ('single', 'Один раз')
        ),
        initial='single'
    )
    amount = forms.IntegerField(min_value=1, initial=1000)
    email = forms.EmailField(required=False)
    comment = forms.CharField(required=False, max_length=1000)
    target = forms.ChoiceField(
        choices=(
            (DONATION_TARGET_LIFE, 'На жизнь'),
            (DONATION_TARGET_ADS, 'На рекламу')
        ),
        initial=DONATION_TARGET_ADS
    )
    success_url = forms.URLField(required=False)
    fail_url = forms.URLField(required=False)

    def __init__(self, data, **kwargs):
        initial = kwargs.get('initial', {})
        data = {**data, **initial}
        super().__init__(data, **kwargs)

class CrowdFundingForm(forms.Form):
    amount = forms.IntegerField(min_value=1, initial=100)
    email = forms.EmailField(required=False)
    name = forms.CharField(required=False)
    comment = forms.CharField(required=False, max_length=1000)
    success_url = forms.URLField(required=False)
    fail_url = forms.URLField(required=False)

    target = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, data, **kwargs):
        initial = kwargs.get('initial', {})
        data = {**data, **initial}
        super().__init__(data, **kwargs)
