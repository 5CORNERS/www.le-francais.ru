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
        with srv.cd(path):
            polly_audios = PollyAudio.objects.select_related('polly').filter(polly__task_status=TASK_STATUS_COMPLETED, polly__url__contains='//s3')
            for chunk in chunks(polly_audios, 100):
                to_save = []
                for polly_audio in chunk:
                    url = polly_audio.polly.url
                    filename = url.split('/')[-1]
                    print(f'{filename}\t{polly_audio.key}')
                    if not srv.exists(filename):
                        response = urllib.request.urlopen(url)
                        with BytesIO() as f:
                            f.write(response.read())
                            f.seek(0)
                            srv.putfo(f, filename)
                    if not 'files.le-francais.ru' in polly_audio.polly.url:
                        polly_audio.polly.url = URL_PATH + filename
                        to_save.append(polly_audio.polly)
                bulk_update(to_save, update_fields=['url'])

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
