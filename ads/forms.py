from django.contrib.auth import get_user_model
from django.db.models import Count
from django.forms import ModelForm, MultipleChoiceField

from ads.models import LineItem

User = get_user_model()


class GeoAdder(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GeoAdder, self).__init__(*args, **kwargs)
        self.fields['targeting_country'] = MultipleChoiceField(
            choices=list(User.objects.values('country_name').order_by(
                'country_name').annotate(
                the_count=Count('country_name')).order_by(
                '-the_count').filter(
                country_name__isnull=False).values_list(
                'country_name', flat=True)[:10]),
            required=False,
        )

    class Meta:
        model = LineItem
        exclude = []
