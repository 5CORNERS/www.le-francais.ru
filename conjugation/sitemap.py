import itertools

from django.contrib.sitemaps import Sitemap
from .models import Verb, ReflexiveVerb
from itertools import chain

class ConjugationSitemap(Sitemap):
    def items(self):
        verb_queryset = Verb.objects.all()
        reflexive_verb_queryset = ReflexiveVerb.objects.all().select_related('verb')
        return list(chain(verb_queryset, reflexive_verb_queryset))

# TODO:add all switch combinations in sitemap
class ConjugationSwitchesSitemap(Sitemap):
    def items(self):
        return list(
            itertools.chain.from_iterable((verb.get_all_urls()
                                           for verb in Verb.objects.all()))
        )

    def location(self, obj):
        return obj
