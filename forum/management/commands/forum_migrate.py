import pickle
#import ggroups2pybbm.forum_classes
from forum_classes import OldForum, OldUser, OldTopic, OldPost
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from pytils.translit import slugify


#from drupango.models import (Node as DrupalNode, Comments as DrupalComments, )
#from html2bbcode import HTML2BBCode

class Command(BaseCommand):
    help = 'Migration phpbb3 to pybbm'

    def handle(self, *args, **options):
        self.migrate_users()
#        self.migrate_categories()
#        self.migrate_forums()
#        self.mirgate_topics()
#        self.migrate_news()
#        self.migrate_blogs()

    def migrate_users(self):
#        old_forum = OldForum()
        with open('ggroups2pybbm/oldforum1.dat','rb') as file:
            old_forum = pickle.load(file)
        count = 0
        for user in old_forum.users:
            count += 1
            if count == 10:
                break
            if user.username == None:
                user.username ="user" + str(count)
            new_user, created = User.objects.get_or_create(
                username=user.username)
            if created:
                new_user.email = user.mail
                new_user.set_password(User.objects.make_random_password())
                new_user.date_joined = user.registration_date
                new_user.last_login = user.last_visit_date
                new_user.save()
