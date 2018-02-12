from django.test import TestCase
from home.models import PageWithSidebar, ArticlePage

class Page2ArticleTestCase(TestCase):
    def setUp(self):
        PageWithSidebar.objects.create(
            path='00010001',
            depth='2',
            slug='slug',
            url_path='home',
            title='title',
            seo_title='seo_title',
            show_in_menus=True,
            menu_title='menu_title',
            is_nav_root=False,
            is_selectable=True,
            reference_title='reference_title',
            subtitle='subtitle',
            live=True,
        )