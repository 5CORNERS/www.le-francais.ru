from datetime import timedelta

from django.core.management import BaseCommand

from ads.utils import clear_session_data
from user_sessions.models import Session
from user_sessions.backends.db import SessionStore
from django_bulk_update import helper

class Command(BaseCommand):
    def handle(self, *args, **options):
        c = Session.objects.count()
        to_update = []
        for i, session in enumerate(Session.objects.all().iterator(), start=1):
            session:Session
            data = session.get_decoded()
            clear_session_data(data)
            session.session_data = SessionStore().encode(data)
            if not 'ads_cappings' in data:
                session.expire_date = session.last_activity + timedelta(days=7)
            if len(data) == 1 and 'Yandex' in data:
                session.expire_date = session.last_activity + timedelta(days=7)
            print(f'{i}/{c}', end='\r')
            if i % 100000 == 0 or i == c:
                print(f'Saving batch {i // 100000 }', end='... ')
                helper.bulk_update(to_update, update_fields=['data', 'expire_date'])
                print('Done!')
                to_update = []
        print('\nDone!')
