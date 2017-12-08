from django.core.management import BaseCommand, CommandError

from home.models import PageWithSidebar, ArticlePage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('arg', type=str, nargs='+')

    def handle(self, *args, **options):
        sidebar_pages = []
        for option in options['arg']:
            try:
                page_id = int(option)
                page = PageWithSidebar.objects.get(id=page_id)
            except:
                try:
                    page_slug = option
                    page = PageWithSidebar.objects.get(slug=page_slug)
                except:
                    raise CommandError('''\nPage with this id or slug "''' + str(option) + '''" doesn't exist''')
            sidebar_pages.append(page)
        service_path = '000100010999'
        service_depth = '3'
        service_slug = 'service_page'
        service_url_path = 'home/service_page'
        for old_page in sidebar_pages:
            new_page = ArticlePage.objects.create(
                path = service_path,
                depth = service_depth,
                slug = service_slug,
                url_path = service_url_path,
                title = old_page.title,
                seo_title = old_page.seo_title,
                show_in_menus = old_page.show_in_menus,
                allow_comments= True,
                menu_title = old_page.menu_title,
                is_nav_root = old_page.is_nav_root,
                is_selectable = old_page.is_selectable,
                reference_title = old_page.reference_title,
                subtitle = old_page.subtitle,
                body = old_page.body,
                live = True,
            )

            old_slug = old_page.slug
            old_path = old_page.path
            old_depth = old_page.depth
            old_url_path = old_page.url_path
            old_page.delete()

            new_page.slug = old_slug
            new_page.path = old_path
            new_page.depth = old_depth
            new_page.url_path = old_url_path
            new_page.save()


