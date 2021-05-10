import os
import random
import string
from pathlib import Path

from django.core.management import BaseCommand

from home.models import LessonPage

FTP_RESUMES_PATH = '/var/www/www-root/data/www/files.le-francais.ru/resumes/'
URL_RESUMES_PATH = '/resumes/'

def to_ftp(filename, file, path):
    import pysftp
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(
        host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
        username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
        password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
        cnopts=cnopts
    )
    with srv.cd(path):
        if srv.exists(filename):
            return True
        if isinstance(file, str):
            file = open(file, 'rb')
            srv.putfo(file, filename)
            file.close()
        else:
            file = file
            file.seek(0)
            try:
                srv.putfo(file, filename)
            except FileNotFoundError as e:
                print(e)
                print(f'ERROR!! FILE NOT FOUND {filename} {path}')
                return False
    return True

class Command(BaseCommand):
    def handle(self, *args, **options):
        path = Path('home/data/à partir de 86')
        for pdf_path in path.glob('*.pdf'):
            random_key = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in
                                 range(10))
            pdf_name = os.path.splitext(os.path.basename(pdf_path.absolute()))[0]
            new_pdf_name = pdf_name + '_' + random_key + '.pdf'
            to_ftp(new_pdf_name, pdf_path.open('rb'), FTP_RESUMES_PATH)
            url = URL_RESUMES_PATH + new_pdf_name
            lesson_number = int(pdf_name.split('_')[0])
            print(lesson_number)
            lesson = LessonPage.objects.get(lesson_number=lesson_number)
            lesson.repetition_material = url
            lesson.save_revision()
            lesson.get_latest_revision().publish()
