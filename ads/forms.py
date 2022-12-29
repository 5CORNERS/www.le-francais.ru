from django.contrib.auth import get_user_model
from django.db.models import Count
from django import forms
from django.utils.encoding import force_text

from ads.models import LineItem

User = get_user_model()

COUNTRIES_CHOICES = [(x[0], x[1]) for x in User.objects.exclude(country_code__isnull=True).values_list('country_code', 'country_name').annotate(count=Count('country_code')).order_by('-count')]
CITIES_CHOICES = [(x[0], x[0]) for x in User.objects.exclude(city__isnull=True).values_list('city').annotate(count=Count('city')).order_by('-count')]


class ArrayMultipleSelected(forms.SelectMultiple):
    def format_value(self, value):
        if value is None and self.allow_multiple_selected:
            return []
        if not isinstance(value, (tuple, list)):
            # This means it should be a comma delimited list of items so parse it
            value = value.split(',')
        return [force_text(v) if v is not None else '' for v in value]

class GeoAdder(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GeoAdder, self).__init__(*args, **kwargs)
        self.fields['targeting_countries'].widget = ArrayMultipleSelected(
            attrs={'class': 'multi-select-input'}, choices=COUNTRIES_CHOICES
        )
        self.fields['targeting_cities'].widget = ArrayMultipleSelected(
            attrs={'class': 'multi-select-input'}, choices=CITIES_CHOICES
        )

    class Meta:
        model = LineItem
        exclude = []
