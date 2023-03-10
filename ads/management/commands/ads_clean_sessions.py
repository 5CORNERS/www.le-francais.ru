from django.core.management import BaseCommand

from ads.utils import clear_session_data
from user_sessions.models import Session
from user_sessions.backends.db import SessionStore

class Command(BaseCommand):
    def handle(self, *args, **options):
        c = Session.objects.count()
        for i, session in enumerate(Session.objects.all()):
            s = SessionStore(session_key=session.pk)
            print(f'{i}/{c}', end='\r')
            clear_session_data(s)
            s.save()
        print('\nDone!')
