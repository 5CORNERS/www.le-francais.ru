# -*- coding: utf-8 -*-
"""Server parity check for the forum editor Markdown converter.

Renders each normalizing fixture (``x.md``) and its normalized form
(``x.expected.md``) with the server renderer (CustomMarkdownParser) and
compares the HTML with whitespace runs collapsed.

Bulk mode (``--db N``): takes N posts from the local database, normalizes
them with ``node forum_editor_src/scripts/normalize.mjs`` (parseMarkdown +
serializeMarkdown) and compares the rendered HTML of the original body and
the normalized Markdown. Prints a summary only; nothing is written to disk.

Run from the repository root (Python 3.7, via micromamba):
    tools\\bin\\micromamba.exe run -p tools\\env python forum_editor_src/scripts/parity.py [--db N]
"""
from __future__ import print_function, unicode_literals

import argparse
import difflib
import glob
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(SRC_ROOT)
FIXTURES = os.path.join(SRC_ROOT, 'test', 'fixtures')
NORMALIZE = os.path.join(HERE, 'normalize.mjs')

WS_RE = re.compile(r'\s+')
# Diff lines start at block-level tags.
LINE_START_RE = re.compile(r'(?=<(?:p|li|ul|ol|blockquote|details|div|h[1-6]|table|tr)\b)')
BLOCK_TAG_RE = re.compile(
    r'\s*(</?(?:p|br|hr|li|ul|ol|dl|dt|dd|blockquote|details|summary|div|h[1-6]'
    r'|table|thead|tbody|tr|th|td)\b[^>]*>)\s*')
# `![a](x "")` renders title=""; the editor writes no title (same tooltip).
EMPTY_TITLE_RE = re.compile(r'(<img\b[^>]*?) title=""')
# Two inline elements wrapping exactly the same content render the same in
# either order (`**[a](x)**` vs `[**a**](x)`, `^^*a*^^` vs `*^^a^^*`).
INLINE = r'(strong|em|ins|del|mark|sup|sub|a)'
NESTED_PAIR_RE = re.compile(
    r'<' + INLINE + r'((?: [^>]*)?)><' + INLINE + r'((?: [^>]*)?)>([^<]*)</\3></\1>')


def _sort_pair(m):
    outer, outer_attrs, inner, inner_attrs, text = m.groups()
    if outer <= inner:
        return m.group(0)
    return '<%s%s><%s%s>%s</%s></%s>' % (inner, inner_attrs, outer, outer_attrs, text, outer, inner)


# Spec §3: known `:shortcode:`s become the Unicode character (rendered as is,
# instead of the server's emojione picture).
EMOJI_IMG_RE = re.compile(r'<img alt="([^"]*)" class="emojione" [^>]*>')
# Spec §3: spoilers are written `???- "Title"`, which adds class "-" (unstyled).
SPOILER_CLASS = '<details class="-">'

# Normalizing fixtures whose server HTML is expected to change, with the
# reason. Their diff is still printed; they do not fail the run.
KNOWN_DIFFERENCES = {
    'fences-without-blank-lines': (
        'the server wraps fences that touch paragraph text in <p> (invalid HTML: '
        '<p><div class="highlight">); the normalized form renders them as blocks'
    ),
    'real-3': (
        'code blocks are always written fenced (spec §3): an indented code block '
        'renders <pre><code> on the server, a fence <div class="highlight"><pre>'
    ),
}


def setup_django():
    sys.path.insert(0, REPO_ROOT)
    os.chdir(REPO_ROOT)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'le_francais.settings.dev'
    import django
    django.setup()
    from forum.markup_engines import CustomMarkdownParser
    return CustomMarkdownParser()


def read_fixture(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        text = f.read()
    # Same convention as roundtrip.test.js: the trailing newline is trimmed.
    return re.sub(r'\r?\n$', '', text)


def collapse(html):
    """Whitespace runs collapsed; whitespace next to block-level tags (where a
    browser does not render it) and empty image titles dropped; emoji
    pictures replaced with their character; spoiler class "-" dropped;
    directly nested inline pairs put in a fixed order."""
    html = WS_RE.sub(' ', html)
    html = BLOCK_TAG_RE.sub(r'\1', html)
    html = EMPTY_TITLE_RE.sub(r'\1', html)
    html = EMOJI_IMG_RE.sub(r'\1', html)
    html = html.replace(SPOILER_CLASS, '<details>')
    html = NESTED_PAIR_RE.sub(_sort_pair, html)
    return html.strip()


def diff(a, b, name_a, name_b, limit=None):
    a_lines = LINE_START_RE.sub('\n', a).strip().split('\n')
    b_lines = LINE_START_RE.sub('\n', b).strip().split('\n')
    lines = list(difflib.unified_diff(a_lines, b_lines, name_a, name_b, lineterm='', n=1))
    if limit is not None:
        lines = [line if len(line) <= 300 else line[:300] + '...' for line in lines[:limit]]
        if len(lines) == limit:
            lines.append('...')
    return '\n'.join(lines)


def check_fixtures(parser):
    failed = 0
    for expected_path in sorted(glob.glob(os.path.join(FIXTURES, '*.expected.md'))):
        source_path = expected_path[:-len('.expected.md')] + '.md'
        name = os.path.basename(source_path)[:-len('.md')]
        source_html = collapse(parser.format(read_fixture(source_path)))
        expected_html = collapse(parser.format(read_fixture(expected_path)))
        if source_html == expected_html:
            print('OK ' + name)
        elif name in KNOWN_DIFFERENCES:
            print('KNOWN %s: %s' % (name, KNOWN_DIFFERENCES[name]))
            print(diff(source_html, expected_html, name + '.md', name + '.expected.md'))
        else:
            failed += 1
            print('DIFF ' + name)
            print(diff(source_html, expected_html, name + '.md', name + '.expected.md'))
    return failed


def fetch_posts(count):
    """Deterministic sample: the newest posts plus every post using syntax
    the converter treats specially (spoilers, tables, fences, images)."""
    from django.db import connection
    query = (
        'SELECT id, body FROM pybb_post WHERE id IN ('
        ' (SELECT id FROM pybb_post ORDER BY id DESC LIMIT %s)'
        ' UNION'
        " (SELECT id FROM pybb_post WHERE body LIKE '%%???%%' OR body LIKE '%%|%%'"
        "  OR body LIKE '%%```%%' OR body LIKE '%%![%%' ORDER BY id DESC LIMIT %s)"
        ') ORDER BY id DESC'
    )
    with connection.cursor() as cursor:
        cursor.execute(query, [count, count])
        return cursor.fetchall()


def normalize(bodies):
    proc = subprocess.Popen(
        ['node', NORMALIZE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=REPO_ROOT,
        shell=(os.name == 'nt'),
    )
    out, _ = proc.communicate(json.dumps(bodies).encode('utf-8'))
    if proc.returncode != 0:
        raise RuntimeError('normalize.mjs exited with code %d' % proc.returncode)
    return json.loads(out.decode('utf-8'))


def check_db(parser, count):
    posts = fetch_posts(count)
    bodies = [body.replace('\r\n', '\n').replace('\r', '\n') for _, body in posts]
    results = normalize(bodies)
    identical = 0
    threw = []
    differ = []
    for (post_id, _), body, result in zip(posts, bodies, results):
        if not result['ok']:
            threw.append((post_id, result['error']))
            continue
        original = collapse(parser.format(body))
        normalized = collapse(parser.format(result['out']))
        if original == normalized:
            identical += 1
        else:
            differ.append((post_id, original, normalized))

    print('posts: %d  identical: %d  parse-threw: %d  differ: %d'
          % (len(posts), identical, len(threw), len(differ)))
    for post_id, error in threw:
        print('THREW %s: %s' % (post_id, error))
    for post_id, original, normalized in differ[:20]:
        print('DIFF %s' % post_id)
        print(diff(original, normalized, 'body', 'normalized', limit=16))
    if len(differ) > 20:
        print('... and %d more: %s' % (len(differ) - 20, ' '.join(str(d[0]) for d in differ[20:])))
    return len(differ)


def main():
    args = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    args.add_argument('--db', type=int, metavar='N', default=0,
                      help='also check N posts from the local database (summary only)')
    options = args.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = setup_django()
    failed = check_fixtures(parser)
    if options.db:
        # Report only: known accepted limits always leave some differences.
        check_db(parser, options.db)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
