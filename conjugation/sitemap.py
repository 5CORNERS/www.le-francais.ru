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
    def get_urls(self, page=1, site=None, protocol=None):
        ...

# TODO:add all switch combinations in sitemap
class ConjugationSwitchesSitemap(Sitemap):
    def get_urls(self, page=1, site=None, protocol=None):
        ...

# TODO:add all switch combinations in sitemap
class ConjugationSwitchesSitemap(Sitemap):
    def get_urls(self, page=1, site=None, protocol=None):
        ...

# TODO:add all switch combinations in sitemap
class ConjugationSwitchesSitemap(Sitemap):
    def get_urls(self, page=1, site=None, protocol=None):
        ...
