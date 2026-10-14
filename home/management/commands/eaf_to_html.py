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
        parser.add_argument('-f', '--filepath', dest='filepath', help='Path to .eaf or .docx file')
        parser.add_argument('-s', '--separate', dest='separate_speech', default=False, action='store_true')

    def handle(self, *args, **options):
        main(file_path=options['filepath'], separate_speech=options['separate_speech'])


def main(file_path, separate_speech=True):
    file_name_without_extension = file_path.rsplit('.', 1)[0]
    if file_path.lower().endswith('.docx'):
        with open(file_path, 'rb') as f:
            document = docx.Document(f)
    else:
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

    preview_html = (
        '<!DOCTYPE html>\n'
        '<html lang="fr">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '    <title>Preview</title>\n'
        '    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">\n'
        '    <style>\n'
        '        body { padding: 40px 20px; max-width: 900px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #212529; }\n'
        '        .bs-callout { padding: 15px; border: 1px solid #eee; border-left-width: 5px; border-radius: 4px; margin: 15px 0; background-color: #fafbfc; }\n'
        '        .bs-callout-info { border-left-color: #17a2b8; }\n'
        '        blockquote.font-italic { margin-top: 1rem; margin-bottom: 1rem; }\n'
        '        .transcript-line { transition: background-color 0.2s; }\n'
        '        .transcript-line:hover { background-color: #fff9c4; cursor: pointer; }\n'
        '    </style>\n'
        '</head>\n'
        '<body>\n'
        + html + '\n'
        '</body>\n'
        '</html>\n'
    )
    with open(f'{file_name_without_extension}_preview.html', 'w', encoding='utf-8') as preview_file:
        preview_file.write(preview_html)

