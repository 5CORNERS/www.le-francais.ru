from django.core.management.base import BaseCommand
from home.models import DefaultPage, PageWithSidebar, LessonPage
from ._private import set_block


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.find_urls(DefaultPage)
        self.find_urls(PageWithSidebar)
        self.find_urls(LessonPage)


    def find_urls(self, x):
        for page in x.objects.all():
            for i in range(len(page.body.stream_data)):
                block = page.body.__getitem__(i)
                if block.block_type == 'html':
                    block.value = block.value.replace('http://www.le-francais.ru/', '/')
                    set_block(i, block, page.body)
            self.stdout.write('save page' + page.url_path)
            page.save()
