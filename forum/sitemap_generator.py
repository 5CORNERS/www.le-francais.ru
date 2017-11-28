from math import ceil

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from pybb.models import Forum, Topic


class TopicPages:
    def __init__(self, queryset):
        self.pages = []
        for topic in queryset:
            page_count = int(ceil(topic.post_count / settings.PYBB_TOPIC_PAGE_SIZE))
            for i in range(page_count):
                self.pages.append(TopicPage(topic.id, i + 1, topic.updated))


class TopicPage:
    def __init__(self, pk, num, updated):
        self.pk = pk
        self.num = num
        self.updated = updated


class ForumSitemap(Sitemap):
    def items(self):
        return Forum.objects.filter(hidden=False, category__hidden=False)

    def lastmod(self, obj):
        return obj.updated


class TopicSitemap(Sitemap):
    def items(self):
        queryset = Topic.objects.filter(on_moderation=False, forum__hidden=False, forum__category__hidden=False)
        objects = TopicPages(queryset)
        return objects.pages

    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        return reverse('topic', kwargs={'pk': obj.pk}) + '?page=%s' % obj.num
