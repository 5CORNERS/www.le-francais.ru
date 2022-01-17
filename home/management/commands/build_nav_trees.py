from django.core.management import BaseCommand
from wagtail.core.models import Page

from home.models import PageWithSidebar, LessonPage, ArticlePage, PodcastPage
from home.utils import get_nav_tree

def is_nav_root(page: Page) -> bool:
	if isinstance(page, PageWithSidebar) and page.is_nav_root:
		return True
	elif isinstance(page, LessonPage) and page.is_nav_root:
		return True
	elif isinstance(page, ArticlePage) and page.is_nav_root:
		return True
	elif isinstance(page, PodcastPage):
		return False
	else:
		return False


def get_nav_root(page: Page) -> Page:
    current_page = page
    while not is_nav_root(current_page):
        if current_page.get_parent() is None:
            break
        current_page = current_page.get_parent().specific
    return current_page

class Command(BaseCommand):
	def handle(self, *args, **options):
		for page in Page.objects.all().order_by('-last_published_at'):
			print(page.title)
			root = get_nav_root(page)
			page_tree = page.nav_tree
			page_tree.tree = get_nav_tree(
				root = root,
				current_page=page
			)
			page_tree.save()
