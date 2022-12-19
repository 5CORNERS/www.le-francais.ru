import os
from io import BytesIO
from stat import S_ISREG
from urllib import request, error

import pysftp
from django.core.management import BaseCommand
from django_bulk_update.helper import bulk_update

from conjugation.models import PollyAudio
from polly.const import COMPLETED as TASK_STATUS_COMPLETED

import time

URL_PATH = 'https://files.le-francais.ru/conjugaison/polly/'


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = time.time()
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
            files = [f.filename for f in srv.listdir_attr() if S_ISREG(f.st_mode)]
            polly_audios = PollyAudio.objects.select_related('polly').filter(polly__task_status=TASK_STATUS_COMPLETED,
                                                                             polly__url__contains='//s3')
            i = input(f'There are {polly_audios.count()} files to save. Start now?')
            if i in ['n', 'N', '0']:
                raise SystemExit
            for chunk in chunks(polly_audios, 100):
                print(f'====================================================')
                to_save = []
                for polly_audio in chunk:
                    print(f'----------------------------------------------------')
                    url = polly_audio.polly.url
                    filename = url.split('/')[-1]
                    print(f'{filename}\t{polly_audio.key}')
                    try:
                        if not filename in files:
                            print(f'FILE NOT FOUND')
                            start_time = time.time()
                            response = request.urlopen(url)
                            print(f'Getting File: {time.time() - start_time}')
                            with BytesIO() as f:
                                start_time = time.time()
                                f.write(response.read())
                                f.seek(0)
                                srv.putfo(f, filename)
                                print(f'Putting File: {time.time() - start_time}')
                        else:
                            print(f'FILE ALREADY EXIST')
                        if not 'files.le-francais.ru' in polly_audio.polly.url:
                            polly_audio.polly.url = URL_PATH + filename
                            to_save.append(polly_audio.polly)

                    except error.HTTPError as e:
                        print(f'ERROR:\n'
                              f'CODE: {e.code}\n'
                              f'MSG: {e.msg}\n'
                              f'URL: {e.filename}')

                print('SAVING TO DATABASE')
                start_time = time.time()
                bulk_update(to_save, update_fields=['url'])
                print(f'Saving chunk: {time.time() - start_time}')


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
