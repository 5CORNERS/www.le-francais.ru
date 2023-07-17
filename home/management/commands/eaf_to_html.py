import json

import docx
from django.core.management import BaseCommand

from home.utils import docx_parse_document
from home.utils import eaf_to_docx

EAF_FILE_NAME = 'Ani.eaf'
FILE_NAME_WITHOUT_EXTENSION = EAF_FILE_NAME.rsplit('.', 1)[0]


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        :type parser:  argparse.ArgumentParser
        """
        parser.add_argument('-f --filepath', dest='filepath')
        parser.add_argument('-s --separate', dest='separate_speech', default=False, action='store_true')

    def handle(self, *args, **options):
        main(file_path=options['filepath'], separate_speech=options['separate_speech'])


def main(file_path, separate_speech=True):
    file_name_without_extension = file_path.rsplit('.', 1)[0]
    with open(file_path, 'rb') as eaf_file:
        eaf_docx = eaf_to_docx(eaf_file, True, separate_speech)
    with open(f'{file_name_without_extension}.docx',
              'wb') as docx_file:
        docx_file.write(eaf_docx.read())

    with open(f'{file_name_without_extension}.docx', 'rb') as f:
        document = docx.Document(f)
    html, transcript_map = docx_parse_document(document)

    with open(f'{file_name_without_extension}.json', 'w', encoding='utf-8') as map_json_file:
        json.dump(transcript_map, map_json_file)

    if separate_speech:
        html = html.replace('<p>— ', '<p>').replace('</p><p>', '\n').replace('</p>', '').replace('<p>', '')
    with open(f'{file_name_without_extension}.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html)
