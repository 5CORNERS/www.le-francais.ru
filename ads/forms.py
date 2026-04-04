from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django import forms

# Forward compatibility for modern Django
try:
    from django.utils.encoding import force_str
except ImportError:
    from django.utils.encoding import force_text as force_str

from ads.models import LineItem
User = get_user_model()

class ArrayMultipleSelected(forms.SelectMultiple):
    def format_value(self, value):
        if value is None:
            return []

        if not isinstance(value, (tuple, list)):
            # Safely verify it's a string before splitting
            if isinstance(value, str):
                value = value.split(',')
            else:
                value = [value]

        return [force_str(v) if v is not None else '' for v in value]


class GeoAdder(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GeoAdder, self).__init__(*args, **kwargs)

        # 1. Queries evaluate dynamically when form is created
        # 2. Excludes empty strings ("") along with NULLs
        countries_choices = [
            (x[0], x[1]) for x in User.objects.exclude(
                Q(country_code__isnull=True) | Q(country_code__exact='')
            ).values_list('country_code', 'country_name').annotate(
                count=Count('country_code')
            ).order_by('-count')
        ]

        cities_choices = [
            (x[0], x[0]) for x in User.objects.exclude(
                Q(city__isnull=True) | Q(city__exact='')
            ).values_list('city').annotate(
                count=Count('city')
            ).order_by('-count')
        ]

        self.fields['targeting_countries'].widget = ArrayMultipleSelected(
            attrs={'class': 'multi-select-input'},
            choices=countries_choices
        )
        self.fields['targeting_cities'].widget = ArrayMultipleSelected(
            attrs={'class': 'multi-select-input'},
            choices=cities_choices
        )

    class Meta:
        model = LineItem
        exclude = []
