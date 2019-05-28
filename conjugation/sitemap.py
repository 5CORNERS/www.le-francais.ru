from django.contrib.sitemaps import Sitemap
from .models import Verb, ReflexiveVerb
from itertools import chain

class ConjugationSitemap(Sitemap):
    def items(self):
        verb_queryset = Verb.objects.all()
        reflexive_verb_queryset = ReflexiveVerb.objects.all().select_related('verb')
        return list(chain(verb_queryset, reflexive_verb_queryset))
