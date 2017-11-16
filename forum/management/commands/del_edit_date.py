from django.core.management import BaseCommand
from custom_user.models import User
from pybb.models import Post
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        for post in Post.objects.all():
            print(str(post.id) + '\t' + str(post.updated))
            if post.updated != None:
                post.updated = None
                post.save()

        # print()
        # user = User.objects.get(username='Французский язык с удовольствием')
        # for post in Post.objects.filter(user=user):
        #     print (str(post.id)+ '\t' + str(post.created))
        #     if post.created > datetime(2017,9,21):
        #         post.created = datetime(2011,1,1)
        #         post.save()


