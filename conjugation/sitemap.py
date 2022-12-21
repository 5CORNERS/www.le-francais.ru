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
    limit=500
    def items(self):
        verb_queryset = Verb.objects.all().order_by('-count')
        return verb_queryset

    def location(self, obj):
        return obj.get_all_urls()

    def _urls(self, page, protocol, domain):
        urls = []
        latest_lastmod = None
        all_items_lastmod = True
        for item in self.paginator.page(page).object_list:
            first_url = True
            for url in item.get_all_urls():
                loc = "%s://%s%s" % (
                protocol, domain, url)
                if first_url:
                    priority = 0.6
                    first_url = False
                else:
                    priority = 0.5
                lastmod = None
                if all_items_lastmod:
                    all_items_lastmod = lastmod is not None
                    if (all_items_lastmod and
                            (
                                    latest_lastmod is None or lastmod > latest_lastmod)):
                        latest_lastmod = lastmod
                url_info = {
                    'item': item,
                    'location': loc,
                    'lastmod': lastmod,
                    'changefreq': None,
                    'priority': str(priority if priority is not None else ''),
                }
                urls.append(url_info)
        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod
        return urls

