from django.core.management import BaseCommand

from ads.utils import clear_session_data
from user_sessions.models import Session
from user_sessions.backends.db import SessionStore

class Command(BaseCommand):
    def handle(self, *args, **options):
        c = Session.objects.count()
        for i, session_key in enumerate(Session.objects.values_list('session_key', flat=True)):
            s = SessionStore(session_key=session_key.pk)
            print(f'{i}/{c}', end='\r')
            clear_session_data(s)
            s.save()
        print('\nDone!')
