import os
import urllib
from io import BytesIO

import pysftp
from django.core.management import BaseCommand
from django_bulk_update.helper import bulk_update

from conjugation.models import PollyAudio
from polly.const import TASK_STATUS_COMPLETED

URL_PATH = 'https://files.le-francais.ru/conjugaison/polly/'

class Command(BaseCommand):
    def handle(self, *args, **options):
        path = '/var/www/www-root/data/www/files.le-francais.ru/conjugaison/polly/'
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        srv = pysftp.Connection(
            host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
            username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
            password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
            cnopts=cnopts
        )
        to_save = []
        with srv.cd(path):
            for polly_audio in PollyAudio.objects.select_related('polly').filter(polly__task_status=TASK_STATUS_COMPLETED):
                url = polly_audio.polly.url
                filename = url.split('/')[-1]
                print(filename)
                if not srv.exists(filename):
                    response = urllib.request.urlopen(url)
                    with BytesIO() as f:
                        f.write(response.read())
                        f.seek(0)
                        srv.putfo(f, filename)
                polly_audio.polly.url = URL_PATH + filename
                to_save.append(polly_audio.polly)
        bulk_update(to_save, update_fields=['url'])

