from django.core.management import BaseCommand
from home.models import LessonPage
from ._private import create_redirect
from wagtail.wagtailredirects.models import Redirect


class Command(BaseCommand):

    def handle(self, *args, **options):
        # self.create_redirects()
        self.make_permanent()
        # self.fix_redirects()

    def create_redirects(self):
        for page in LessonPage.objects.all():
            create_redirect(page.url_path.lstrip('/home'), page.id,False)

    def make_permanent(self):
        for redirect in Redirect.objects.all():
            if redirect.is_permanent == False:
                print(redirect)
                redirect.is_permanent = True
                redirect.save()

    def fix_redirects(self):
        for redirect in Redirect.objects.all():
            if redirect.old_path[0:5] == '/home':
                redirect.old_path ='/' + redirect.old_path.lstrip('/home')
                redirect.is_permanent = False
                redirect.save()
            if redirect.old_path[-1] == '/':
                redirect.old_path = redirect.old_path.rstrip('/')
                redirect.save()

