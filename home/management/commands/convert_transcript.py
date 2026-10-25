"""
Convert a lesson transcript DOCX into admin files:
  <Prefix>-admin.html, <Prefix>-admin.json and <Prefix>-masterfile.json

  manage.py convert_transcript 4
  manage.py convert_transcript "2020-11-19 - Lecon_003_Xv.docx" French-003 --db
"""
import json
import os
import re
import time

import docx
from django.core.management import BaseCommand, CommandError

from home.utils import docx_parse_document

DEFAULT_DOCX_DIR = r'C:\Users\ILYA\Dropbox\TRANSCRIBING\DOCX'
DEFAULT_OUTPUT_DIR = r'C:\Users\ILYA\Dropbox\TRANSCRIBING\JSON'

LESSON_NUMBER_RE = re.compile(r'(?:le[cç]on|lesson|french|урок)[_\-\s]*0*(\d+)', re.IGNORECASE)


def extract_lesson_number(filename):
    """Lesson number from names like Lecon_004, French-004, Lesson 3, Урок_3; dates are ignored."""
    m = LESSON_NUMBER_RE.search(os.path.basename(filename))
    return int(m.group(1)) if m else None


def resolve_docx_path(user_input, docx_dir):
    """Find the DOCX by path, by file name (with or without .docx) in docx_dir, or by lesson number."""
    clean_input = user_input.strip('"\'')
    names = [clean_input]
    if not clean_input.lower().endswith('.docx'):
        names.append(clean_input + '.docx')
    for name in names:
        for candidate in (name, os.path.join(docx_dir, name)):
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)

    if clean_input.isdigit() and os.path.isdir(docx_dir):
        lesson_number = int(clean_input)
        for f in sorted(os.listdir(docx_dir)):
            if f.lower().endswith('.docx') and extract_lesson_number(f) == lesson_number:
                return os.path.join(docx_dir, f)
    return None


def update_lesson_page(page, html, lines_map):
    page.transcript_html = html
    page.transcript = list(lines_map)
    page.has_transcript = True
    page.save()


class Command(BaseCommand):
    help = 'Convert a lesson transcript DOCX into admin HTML/JSON files (and optionally update the LessonPage).'

    def add_arguments(self, parser):
        """
        :type parser:  argparse.ArgumentParser
        """
        parser.add_argument('source', help='Lesson number (e.g. 4), DOCX file name (e.g. Lecon_004_V.docx) or path')
        parser.add_argument('prefix', nargs='?', default=None, help='Output prefix (default: French-<NNN>)')
        parser.add_argument('--db', '-u', dest='db', action='store_true',
                            help='Also store the transcript in the LessonPage with this lesson number')
        parser.add_argument('--docx-dir', dest='docx_dir', default=DEFAULT_DOCX_DIR,
                            help=f'Folder to look up DOCX files in (default: {DEFAULT_DOCX_DIR})')
        parser.add_argument('--output-dir', dest='output_dir', default=DEFAULT_OUTPUT_DIR,
                            help=f'Folder to write the output files to (default: {DEFAULT_OUTPUT_DIR})')

    def handle(self, *args, **options):
        t0 = time.time()
        docx_path = resolve_docx_path(options['source'], options['docx_dir'])
        if not docx_path:
            raise CommandError(f"Could not find file '{options['source']}' (checked in {options['docx_dir']}).")

        lesson_number = extract_lesson_number(docx_path)
        out_prefix = options['prefix']
        if not out_prefix:
            out_prefix = (f'French-{lesson_number:03d}' if lesson_number
                          else os.path.splitext(os.path.basename(docx_path))[0])
        output_dir = options['output_dir']

        self.stdout.write('=== Converting Transcript ===')
        self.stdout.write(f'  Source file:   {docx_path}')
        self.stdout.write(f'  Output prefix: {out_prefix}')
        self.stdout.write(f'  Target dir:    {output_dir}')

        try:
            document = docx.Document(docx_path)
        except Exception as e:
            raise CommandError(f'Failed to read DOCX: {e}')
        try:
            html, lines_map = docx_parse_document(document, strict=True)
        except ValueError as e:
            raise CommandError(f'Strict parsing failed: {e}')

        master_data = {
            'lesson_number': lesson_number,
            'docx_source': os.path.basename(docx_path),
            'converted_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'transcript': list(lines_map),
            'transcript_html': html,
        }
        outputs = (
            ('admin.html', html),
            ('admin.json', json.dumps(list(lines_map), ensure_ascii=False)),
            ('masterfile.json', json.dumps(master_data, ensure_ascii=False, indent=2)),
        )
        os.makedirs(output_dir, exist_ok=True)
        for suffix, content in outputs:
            path = os.path.join(output_dir, f'{out_prefix}-{suffix}')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.stdout.write(f'  [OK] Created: {path}')

        if options['db']:
            if not lesson_number:
                raise CommandError(f'Cannot update the database: no lesson number in "{docx_path}".')
            from home.models import LessonPage
            page = LessonPage.objects.filter(lesson_number=lesson_number).first()
            if not page:
                raise CommandError(f'LessonPage with lesson_number={lesson_number} not found.')
            update_lesson_page(page, html, lines_map)
            self.stdout.write(f'  [OK] Updated LessonPage #{lesson_number} (id={page.id}).')

        self.stdout.write(self.style.SUCCESS(f'Completed in {time.time() - t0:.2f}s'))
