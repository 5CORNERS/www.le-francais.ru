from django.core.management import BaseCommand, CommandError

from wagtail.wagtailcore.models import Page

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        table = self.import_table(options['file_path'][0])
        for key in table.keys():
            page = Page.objects.get(id = key)
            self.stdout.write(page.slug, ending='   ')
            self.stdout.write(page.path, ending='	to')
            self.change_path(page, table[key])


    def change_path(self, page, new_path):
        old_path = page.path
        second_page = self.find_page_by_path(new_path)
        if second_page == None:
            self.stdout.write('no second page found!')
            page.path = new_path
            page.save()
        else:
            page.path = '0002'
            page.save()
            second_page.path = old_path
            second_page.save()
            page.path = new_path
            page.save()
        self.stdout.write('	'+ page.path)


    def find_page_by_path(self, p):
        try:
            page = Page.objects.get(path = p)
            return page
        except:
            return None

    def import_table(self, fp):
            d = {}
            with open(fp,'r',encoding='utf-8') as f:
                for line in f:
                    (key, val) = line.rstrip('\n').split(';')
                    d[int(key)] = val
                return d

