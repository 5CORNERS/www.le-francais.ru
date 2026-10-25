#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOCX Transcript Converter for Le-Francais.ru.
Reads DOCX from: C:\\Users\\ILYA\\Dropbox\\TRANSCRIBING\\DOCX\\
Writes exact 3 files to: C:\\Users\\ILYA\\Dropbox\\TRANSCRIBING\\JSON\\
  1. <Prefix>-admin.html
  2. <Prefix>-admin.json
  3. <Prefix>-masterfile.json
"""

import os
import sys
import re
import json
import time
import argparse

DOCX_DIR = r'C:\Users\ILYA\Dropbox\TRANSCRIBING\DOCX'
OUTPUT_DIR = r'C:\Users\ILYA\Dropbox\TRANSCRIBING\JSON'

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'le_francais.settings.dev')

try:
    import django
    django.setup()
except Exception as e:
    print(f"[ERROR] Failed to initialize Django: {e}", file=sys.stderr)
    sys.exit(1)

import docx
from home.utils import docx_parse_document


def resolve_docx_path(user_input):
    clean_input = user_input.strip('\"\'')

    # 1. Direct path exists?
    if os.path.isabs(clean_input) and os.path.exists(clean_input):
        return os.path.abspath(clean_input)

    # 2. Check in DOCX_DIR
    in_docx_dir = os.path.join(DOCX_DIR, clean_input)
    if os.path.exists(in_docx_dir):
        return os.path.abspath(in_docx_dir)

    # 3. Try adding .docx extension
    if not clean_input.lower().endswith('.docx'):
        with_ext = clean_input + '.docx'
        if os.path.exists(with_ext):
            return os.path.abspath(with_ext)
        in_docx_with_ext = os.path.join(DOCX_DIR, with_ext)
        if os.path.exists(in_docx_with_ext):
            return os.path.abspath(in_docx_with_ext)

    # 4. If a pure number was passed (e.g. "4"), look for Lecon_004*.docx in DOCX_DIR
    if clean_input.isdigit():
        num = int(clean_input)
        num_str = str(num).zfill(3)
        if os.path.exists(DOCX_DIR):
            for f in os.listdir(DOCX_DIR):
                if f.endswith('.docx') and (num_str in f or f'_{num}_' in f or f'-{num}-' in f or f'Урок_{num}' in f):
                    return os.path.join(DOCX_DIR, f)

    return None


def extract_lesson_number(docx_path):
    filename = os.path.basename(docx_path)
    # Match Lecon_004, French-004, Lesson_003, Урок_3, etc.
    m = re.search(r'(?:lecon|lesson|french|урок)?[_\-\s]*0*(\d+)', filename, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def convert_docx(docx_path, out_prefix=None, update_db=False):
    t0 = time.time()
    if not os.path.exists(docx_path):
        print(f"[ERROR] File not found: {docx_path}", file=sys.stderr)
        return False

    lesson_num = extract_lesson_number(docx_path)
    num_str = str(lesson_num).zfill(3) if lesson_num else "000"

    if not out_prefix:
        if lesson_num:
            out_prefix = f"French-{num_str}"
        else:
            base = os.path.splitext(os.path.basename(docx_path))[0]
            out_prefix = base

    print(f"=== Converting Transcript ===")
    print(f"  Source file:  {docx_path}")
    print(f"  Output prefix: {out_prefix}")
    print(f"  Target dir:   {OUTPUT_DIR}")

    try:
        doc = docx.Document(docx_path)
    except Exception as e:
        print(f"[ERROR] Failed to read DOCX with python-docx: {e}", file=sys.stderr)
        return False

    print("  Parsing transcript and sticky materials (strict mode)...")
    try:
        html, lines_map = docx_parse_document(doc, strict=True)
    except Exception as e:
        print(f"[ERROR] Strict parsing failed: {e}", file=sys.stderr)
        return False

    # 1. Admin HTML
    admin_html = html

    # 2. Admin JSON
    admin_json = json.dumps(list(lines_map), ensure_ascii=False)

    # 3. Masterfile JSON
    master_data = {
        'lesson_number': lesson_num,
        'docx_source': os.path.basename(docx_path),
        'converted_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'transcript': list(lines_map),
        'transcript_html': admin_html
    }
    master_json = json.dumps(master_data, ensure_ascii=False, indent=2)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    p_html = os.path.join(OUTPUT_DIR, f"{out_prefix}-admin.html")
    p_json = os.path.join(OUTPUT_DIR, f"{out_prefix}-admin.json")
    p_master = os.path.join(OUTPUT_DIR, f"{out_prefix}-masterfile.json")

    with open(p_html, 'w', encoding='utf-8') as f:
        f.write(admin_html)
    with open(p_json, 'w', encoding='utf-8') as f:
        f.write(admin_json)
    with open(p_master, 'w', encoding='utf-8') as f:
        f.write(master_json)

    print(f"  [OK] Created: {p_html} ({len(admin_html)} chars)")
    print(f"  [OK] Created: {p_json} ({len(lines_map)} lines)")
    print(f"  [OK] Created: {p_master}")

    if update_db and lesson_num:
        try:
            from home.models import LessonPage
            page = LessonPage.objects.filter(lesson_number=lesson_num).first()
            if page:
                page.transcript_html = admin_html
                page.transcript = admin_json
                page.save()
                print(f"  [OK] Updated LessonPage #{lesson_num} (id={page.id}) in database.")
            else:
                print(f"  [WARN] LessonPage with lesson_number={lesson_num} not found in DB.")
        except Exception as e:
            print(f"  [WARN] Failed to update database: {e}", file=sys.stderr)

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.2f}s!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Convert Lesson DOCX to Admin HTML/JSON files.")
    parser.add_argument('file', nargs='?', help='DOCX file name (e.g. Lecon_004_V.docx) or path')
    parser.add_argument('prefix', nargs='?', default=None, help='Optional output prefix (e.g. French-004)')
    parser.add_argument('--db', '-u', action='store_true', help='Update local database LessonPage row directly')

    args = parser.parse_args()

    if not args.file:
        parser.print_help()
        print("\nExamples:")
        print("  convert_transcript.bat Lecon_004_V.docx")
        print("  convert_transcript.bat \"2020-11-19 - Lecon_003_Xv.docx\" French-003")
        sys.exit(0)

    docx_path = resolve_docx_path(args.file)
    if not docx_path:
        print(f"[ERROR] Could not find file '{args.file}'.", file=sys.stderr)
        print(f"Checked in: {DOCX_DIR}", file=sys.stderr)
        sys.exit(1)

    success = convert_docx(docx_path, out_prefix=args.prefix, update_db=args.db)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
