import logging
import os
import re
from collections import defaultdict
import binascii
from hashlib import md5
from io import BytesIO, StringIO, TextIOWrapper
from typing import List, Dict, Tuple, BinaryIO

import docx
import shortuuid

from anytree import Node
from docx import Document
from django.conf import settings
from docx.styles.style import _ParagraphStyle, _CharacterStyle
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
from lxml.etree import tostring
from markdown import Markdown
from html import escape as html_escape, unescape

from home.consts import COLUMN_TEXT, COLUMN_START, COLUMN_END, COLUMN_SPEAKER, EU_COUNTRIES
from le_francais.settings.base import FILES_LE_FRANCAIS_HTTPS, \
    FILES_LE_FRANCAIS_SITENAME

logger = logging.getLogger(__name__)

ZERO_WIDTH_SPACE = '\u200b'
ZERO_WIDTH_CHARS_RE = re.compile(r'[\u200b\ufeff\u2060\u200c\u200d]')
HEADING_STYLE_RE = re.compile(r'^Heading (\d)$')
LIST_STYLES = {'List Paragraph'}
CALLOUT_STYLES = {'Intense Quote'}
QUOTE_STYLES = {'Quote'}
PARAGRAPH_DIALOGUE_DASH_RE = re.compile(r'^(?:[—–―]|--)\s')



def is_gpt_disabled(request):
    if request is None:
        return True
    session = request.session
    geoip_dict = session.get('geoip', None)
    test_gpt_disabled = request.GET.get('test_gpt_disabled', None)
    if test_gpt_disabled is not None:
        if test_gpt_disabled == '1':
            return True
        else:
            return False
    if ((geoip_dict and (geoip_dict.get('country_code') in os.environ.get('BLOCKED_COUNTRY_CODES').split(',')
                         or geoip_dict.get('country_code') is None))):
        return True
    return False


def files_le_francais_url(path=''):
	if FILES_LE_FRANCAIS_HTTPS:
		return f'https://{FILES_LE_FRANCAIS_SITENAME}{path}'
	else:
		return f'http://{FILES_LE_FRANCAIS_SITENAME}{path}'


def get_signature(params, secret_key=settings.WALLET_ONE_SECRET_KEY):
    """
    Base64(Byte(MD5(Windows1251(Sort(Params) + SecretKey))))
    params - list of tuples [('WMI_CURRENCY_ID', 643), ('WMI_PAYMENT_AMOUNT', 10)]
    """
    icase_key = lambda s: str(s).lower()

    lists_by_keys = defaultdict(list)
    if len(params[0]) == 3:
        for key, value, id in params:
            lists_by_keys[key].append(value)
    else:
        for key, value in params:
            lists_by_keys[key].append(value)

    str_buff = b''
    for key in sorted(lists_by_keys, key=icase_key):
        for value in sorted(lists_by_keys[key], key=icase_key):
            str_buff += str(value).encode('1251')
    str_buff += secret_key.encode('1251')

    md5_string = md5(str_buff).digest()
    return (binascii.b2a_base64(md5_string)[:-1])

def message_left(n, form1='чашечка', form2='чашечки', form5='чашечек'):
    n10 = n%10
    n100 = n%100
    if n == 0:
        return 'Вы израсходовали последнюю чашечку :( Вы можете пополнить их запас в настройках профиля.'.format(form5)
    elif n10 == 1 and n100 != 11:
        return 'У вас есть ещё {0} {1}. Просмотреть свой остаток и пополнить запас вы можете в настройках профиля.'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return 'У вас есть ещё {0} {1}. Просмотреть свой остаток и пополнить запас вы можете в настройках профиля.'.format(str(n), form2)
    else:
        return 'У вас есть ещё {0} {1}. Просмотреть свой остаток и пополнить запас вы можете в настройках профиля.'.format(str(n), form5)

def message(n, form1=' чашечка', form2=' чашечки', form5=' чашечек'):
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return '{0} {1}'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return '{0} {1}'.format(str(n), form2)
    else:
        return '{0} {1}'.format(str(n), form5)


# Letter Avatar https://github.com/CraveFood/avinit

import re

from base64 import b64encode
from xml.sax.saxutils import escape as xml_escape

try:
    import cairosvg
except ImportError:
    cairosvg = None


DEFAULT_FONTS = [
    'HelveticaNeue-Light',
    'Helvetica Neue Light',
    'Helvetica Neue',
    'Helvetica',
    'Arial',
    'Lucida Grande',
    'sans-serif',
]

DEFAULT_SETTINGS = {
    'width': '200',
    'height': '200',
    'radius': '0',
    'font-family': ','.join(DEFAULT_FONTS),
    'font-size': '80',
    'font-weight': '400',
}

SVG_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" pointer-events="none"
     viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" rx="{radius}" style="{style}"></rect>
  <text text-anchor="middle" y="50%" x="50%" dy="0.35em"
        pointer-events="auto" fill="#ffffff" font-family="{font-family}"
        style="{text-style}">{text}</text>
</svg>
""".strip()
SVG_TEMPLATE = re.sub('(\s+|\n)', ' ', SVG_TEMPLATE)


DEFAULT_COLORS = [
    "#1abc9c", "#16a085", "#f1c40f", "#f39c12", "#2ecc71", "#27ae60",
    "#e67e22", "#d35400", "#3498db", "#2980b9", "#e74c3c", "#c0392b",
    "#9b59b6", "#8e44ad", "#bdc3c7", "#34495e", "#2c3e50", "#95a5a6",
    "#7f8c8d", "#ec87bf", "#d870ad", "#f69785", "#9ba37e", "#b49255",
    "#b49255", "#a94136",
]


def _from_dict_to_style(style_dict):
    return '; '.join(['{}: {}'.format(k, v) for k, v in style_dict.items()])


def _get_color(text, colors=None):
    if not colors:
        colors = DEFAULT_COLORS
    color_index = sum(map(ord, text)) % len(colors)
    return colors[color_index]


def get_svg_avatar(text, **kwargs):

    initials = '=)'

    text = text.strip()
    if text:
        split_text = text.split(' ')
        if len(split_text) > 1:
            initials = split_text[0][0] + split_text[-1][0]
        else:
            initials = split_text[0][0]

    opts = DEFAULT_SETTINGS.copy()
    opts.update(kwargs)

    style = {
        'fill': _get_color(text, opts.get('colors')),
        'width': opts.get('width') + 'px',
        'height': opts.get('height') + 'px',
        'rx': opts.get('radius') + 'px',
        '-moz-border-radius': opts.get('radius') + 'px',
    }

    text_style = {
        'font-weight': opts.get('font-weight'),
        'font-size': opts.get('font-size') + 'px',
    }

    return SVG_TEMPLATE.format(**{
        'height': opts.get('height'),
        'width': opts.get('width'),
        'radius': opts.get('radius'),
        'style': _from_dict_to_style(style),
        'font-family': opts.get('font-family'),
        'text-style': _from_dict_to_style(text_style),
        'text': xml_escape(initials.upper()),
    }).replace('\n', '')


def get_png_avatar(text, output_file, **kwargs):
    if not cairosvg:
        raise Exception('CairoSVG is required to png conversions.')

    svg_avatar = get_svg_avatar(text, **kwargs)
    cairosvg.svg2png(svg_avatar, write_to=output_file)


def get_avatar_data_url(text, **kwargs):
    svg_avatar = get_svg_avatar(text, **kwargs)
    b64_avatar = b64encode(svg_avatar.encode('utf-8'))
    return 'data:image/svg+xml;base64,' + b64_avatar.decode('utf-8')

def get_navigation_object_from_page(root, current_page) -> dict:
    page_object = {
        "text": str(root.title),
        "nodes": [],
        "href": root.get_url(),
        "state": {}
    }
    from home.models import PageWithSidebar
    from home.models import LessonPage
    from home.models import ArticlePage
    from home.models import PodcastPage
    if (isinstance(root.specific, PageWithSidebar) or isinstance(root.specific, LessonPage) or isinstance(root.specific, ArticlePage) or isinstance(root.specific, PodcastPage)):
        menu_title = root.specific.menu_title
        if not isinstance(menu_title, str):
            menu_title = menu_title.decode()
        if menu_title != '':
            page_object["text"] = menu_title
        if not getattr(root.specific, 'is_selectable', True):
            page_object["selectable"] = False
    if root.id == current_page.id:
        page_object["state"] = {
            "selected": True
        }
        page_object["selectable"] = False
    for child in root.get_children():
        if child.show_in_menus and child.live:
            page_object["nodes"].append(
                get_navigation_object_from_page(child, current_page))
    if len(page_object["nodes"]) == 0:
        page_object.pop('nodes', None)
    return page_object

def get_nav_tree(root, current_page):
    if root.show_in_menus:
        nav_items = [get_navigation_object_from_page(root, current_page)]
    else:
        navigation_object = get_navigation_object_from_page(root, current_page)
        if 'nodes' in navigation_object:
            nav_items = navigation_object["nodes"]
        else:
            nav_items = []
    return nav_items

def parse_tab_delimited_srt_file(file):
    from csv import DictReader, excel_tab
    from collections import OrderedDict
    result = OrderedDict()
    c = 0
    for row in DictReader(file, dialect=excel_tab):
        b_name = row.get('bookmark') or row.get('Bookmark') or None
        result[row[COLUMN_TEXT]] = {
            "id": f'line{c}',
            "start":row[COLUMN_START],
            "end":row[COLUMN_END],
            "speaker":row[COLUMN_SPEAKER],
            "bookmark": b_name,
            "bookmarks": [b_name] if b_name else []
        }
        c += 1
    #return OrderedDict(sorted(result.items(), key=lambda x: x[1]['start']))
    return result


def sub_html(html:str, parsed_srt):
    import re
    errors = []
    sub_map = []
    cursor=0
    for l, data in parsed_srt.items():
        new_line = f'<span class="transcript-line" ' \
                   f'id="{data["id"]}" ' \
                   f'data-start="{data["start"]}"' \
                   f' data-end="{data["end"]}"' \
                   f' data-speaker="{data["speaker"]}"' \
                   f'>{l}</span>'
        match = re.search(f'({re.escape(l)})', html[cursor:])
        if match is None:
            errors.append(f'NOT FOUND -- {l}')
            continue
        sub_map.append((match.start(1) + cursor, match.end(1) + cursor, new_line))
        cursor += match.end(1)
    for start, end, new_line in reversed(sub_map):
        html = html[:start] + new_line + html[end:]
    return html, errors

def create_document_from_transcript_srt(table_csv) -> BytesIO:
    parsed_table = parse_tab_delimited_srt_file(StringIO(table_csv))
    document = docx.Document()
    last_speaker = None
    bookmark_id = 1
    for l, data in parsed_table.items():
        speaker = data['speaker']
        if speaker != last_speaker:
            current_p:Paragraph = document.add_paragraph('— ')
        else:
            current_p.add_run(' ')

        bookmarks = data.get('bookmarks') or ([] if not data.get('bookmark') else [data['bookmark']])
        opened_bms = []
        for b_name in bookmarks:
            b_start = OxmlElement('w:bookmarkStart')
            b_start.set(qn('w:id'), str(bookmark_id))
            b_start.set(qn('w:name'), str(b_name))
            current_p._p.append(b_start)
            opened_bms.append(bookmark_id)
            bookmark_id += 1

        anchored_l = l if l.startswith(ZERO_WIDTH_SPACE) else f'{ZERO_WIDTH_SPACE}{l}'
        new_run:Run = current_p.add_run(anchored_l)
        comment = new_run.add_comment(
            text=f'{data["speaker"]} {data["start"]} {data["end"]} {data["id"]}'
        )

        for b_id in opened_bms:
            b_end = OxmlElement('w:bookmarkEnd')
            b_end.set(qn('w:id'), str(b_id))
            current_p._p.append(b_end)

        last_speaker = speaker
    file = BytesIO()
    document.save(file)
    file.seek(0)
    return file


def text_postprocessor(html):
    html = ZERO_WIDTH_CHARS_RE.sub('', html)
    html = html \
            .replace(' »', '&nbsp;»')\
            .replace('\u202f»', '&nbsp;»')\
            .replace('« ', '«&nbsp;')\
            .replace('«\u202f', '«&nbsp;')\
            .replace(' ?', '&nbsp;?')\
            .replace('\u202f?', '&nbsp;?')\
            .replace(' !', '&nbsp;!')\
            .replace('\u202f!', '&nbsp;!')
    # Replace space followed by hyphen before letters with non-breaking hyphen
    html = re.sub(r' -([A-Za-zА-Яа-яÀ-ÿ])', r' ‑\g<1>', html)
    return html



def _close_open_block(html, open_block):
    if open_block == 'ul':
        html += '</ul>'
    elif open_block == 'callout':
        html += '</div>'
    elif open_block == 'blockquote':
        html += '</blockquote>'
    return html, None


def docx_parse_document(document):
    html = ""
    lines_map = []
    opened_tags = []
    toc_nodes = []
    open_block = None

    declared_bookmarks = {}
    for p_idx, p in enumerate(document.paragraphs):
        for b_name in p._element.xpath('.//w:bookmarkStart/@*[local-name()="name"]'):
            if b_name != '_GoBack' and b_name not in declared_bookmarks:
                declared_bookmarks[b_name] = p_idx

    for b_name in document._element.xpath('.//w:bookmarkStart/@*[local-name()="name"]'):
        if b_name != '_GoBack' and b_name not in declared_bookmarks:
            declared_bookmarks[b_name] = len(document.paragraphs) + 1

    state = {
        'last_speaker': None,
        'active_bookmarks': [],
        'pending_bookmarks': [],
        'active_replica_entry': None,
        'callout_sticky_until': None,
        'sticky_materials': [],
    }
    for p_idx, p in enumerate(document.paragraphs):
        html, lines_map, opened_tags, open_block = docx_parse_through_paragraph(
            document, p, html, lines_map, opened_tags, toc_nodes,
            open_block=open_block, state=state, p_index=p_idx
        )
    if open_block:
        html, open_block = _close_open_block(html, open_block)

    # Validate sticky materials
    seen_stickies = set()
    for sticky in state.get('sticky_materials', []):
        target = sticky['anchor']
        mat_idx = sticky['p_index']
        if (target, mat_idx) in seen_stickies:
            continue
        seen_stickies.add((target, mat_idx))

        snippet = sticky.get('snippet', '')
        if target not in declared_bookmarks:
            raise ValueError(f"Sticky material in block '{snippet}' references non-existent anchor/bookmark '{target}'.")
        target_p_idx = declared_bookmarks[target]
        if target_p_idx <= mat_idx:
            logger.warning(
                f"Sticky material in block '{snippet}' references anchor '{target}' "
                f"which appears before or at the material itself (material at paragraph {mat_idx}, anchor at paragraph {target_p_idx})."
            )

    html = re.sub('!\[(.+?)]\((.+?)\s&quot;(.+?)&quot;\)',
                  '<img title="\g<1>" src="\g<2>" alt="\g<3>">', html)
    def _replace_html_block(match):
        sticky_anchor = match.group(1)
        html_block = unescape(match.group(2))
        if sticky_anchor:
            tag_end = html_block.find('>')
            if tag_end != -1:
                html_block = html_block[:tag_end] + f' data-sticky-until="{sticky_anchor}"' + html_block[tag_end:]
        return html_block

    html = re.sub(r'<p>\[HTML(?:\s+data-sticky-until="([^"]+)")?\](.*?)\[/HTML\]</p>', _replace_html_block, html, flags=re.DOTALL)
    html = text_postprocessor(html)
    # Split lines containing '||' with proportional timestamp distribution
    final_lines_map = []
    for entry in lines_map:
        raw_text = entry.get('text', '')
        if '||' in raw_text:
            raw_parts = raw_text.split('||')
            parts = [p.strip() for p in raw_parts if p.strip()]
            if len(parts) > 1:
                total_start = int(entry['start'])
                total_end = int(entry['end'])
                total_duration = total_end - total_start
                total_len = sum(len(p) for p in parts)
                current_start = total_start
                generated_sub_entries = []
                for idx, part_text in enumerate(parts):
                    if idx == len(parts) - 1:
                        part_end = total_end
                    else:
                        dur = int(round(total_duration * len(part_text) / float(total_len))) if total_len > 0 else total_duration // len(parts)
                        part_end = min(current_start + dur, total_end)
                    sub_entry = {
                        'id': f"{entry['id']}-p{idx + 1}" if idx > 0 else entry['id'],
                        'speaker': entry['speaker'],
                        'start': str(current_start),
                        'end': str(part_end),
                        'text': part_text,
                        'bookmark': entry.get('bookmark') if idx == 0 else None,
                        'bookmarks': entry.get('bookmarks', []) if idx == 0 else [],
                        'is_split': True,
                        'split_index': idx,
                        'split_adjacent': (idx > 0),
                    }
                    generated_sub_entries.append(sub_entry)
                    final_lines_map.append(sub_entry)
                    current_start = part_end

                # Synchronize HTML: split the single DOM span into multiple spans matching generated_sub_entries
                entry_id = entry['id']
                span_pattern = rf'<span class="transcript-line"[^>]*id="{re.escape(entry_id)}"[^>]*>(.*?)</span>'
                span_match = re.search(span_pattern, html, flags=re.DOTALL)
                if span_match:
                    full_span_str = span_match.group(0)
                    inner_html = span_match.group(1)
                    if '||' in inner_html:
                        inner_parts = inner_html.split('||')
                        if len(inner_parts) == len(generated_sub_entries):
                            replacement_spans = []
                            for idx, sub_e in enumerate(generated_sub_entries):
                                p_content = inner_parts[idx].strip()
                                spk = sub_e['speaker']
                                s_id = sub_e['id']
                                s_st = sub_e['start']
                                s_en = sub_e['end']
                                replacement_spans.append(
                                    f'<span class="transcript-line" id="{s_id}" data-start="{s_st}" data-end="{s_en}" data-speaker="{spk}">{p_content}</span>'
                                )
                            html = html.replace(full_span_str, ' '.join(replacement_spans), 1)
                continue
            else:
                entry['text'] = raw_text.replace('||', '').strip()
        final_lines_map.append(entry)
    lines_map = final_lines_map

    # Strip any remaining literal || markers from rendered html
    html = html.replace('||', '')

    return html, lines_map

def docx_parse_through_paragraph(document, paragraph:Paragraph, html, lines_map, opened_tags, toc_nodes,
                                 open_block=None, state=None, p_index=0):
    if state is None:
        state = {'last_speaker': None, 'active_bookmarks': [], 'pending_bookmarks': [], 'active_replica_entry': None, 'callout_sticky_until': None, 'sticky_materials': []}
    p_html = ''
    p_map = []
    runs_iterator = (run for run in paragraph.runs)

    cleaned_p_text = ZERO_WIDTH_CHARS_RE.sub('', paragraph.text).lstrip()
    starts_with_dash = bool(PARAGRAPH_DIALOGUE_DASH_RE.match(cleaned_p_text))
    p_context = {
        'starts_with_dash': starts_with_dash,
        'paragraph_speaker': None,
        'current_replica_entry': state.get('active_replica_entry'),
        'state': state,
    }
    if state.get('active_replica_entry') is not None and paragraph.text.strip():
        curr_text = state['active_replica_entry']['text']
        if curr_text and not curr_text.endswith(' ') and not curr_text.endswith('||'):
            state['active_replica_entry']['text'] += ' '

    opening_tags_html = ''
    if opened_tags:
        for tag in opened_tags:
            attrs = "".join((f' {attr}="{value}"' for attr, value in tag['attrs'].items()))
            opening_tags_html += f'<{tag["name"]}{attrs}>'

    p_html, p_map, opened_tags = xml_parse_through_element(
        document, runs_iterator, paragraph._element, p_html, p_map, opened_tags,
        p_context=p_context
    )

    closing_tags_html = ''
    if opened_tags:
        for tag in opened_tags:
            closing_tags_html += f'</{tag["name"]}>'

    # fixing out of place characters
    p_html = re.sub('([a-zA-Z])(<span.*?>)', '\g<2>\g<1>', p_html)
    p_html = re.sub('(</span>)([.,:])', '\g<2>\g<1>', p_html)

    p_style: _ParagraphStyle = paragraph.style
    style_name = getattr(p_style, 'name', '') or ''

    heading_match = HEADING_STYLE_RE.match(style_name)
    target_block = None
    if style_name in LIST_STYLES:
        target_block = 'ul'
    elif style_name in CALLOUT_STYLES:
        target_block = 'callout'
    elif style_name in QUOTE_STYLES:
        target_block = 'blockquote'

    if open_block and open_block != target_block:
        html, open_block = _close_open_block(html, open_block)
        if state:
            state['callout_sticky_until'] = None

    if heading_match:
        heading_value = int(heading_match.group(1))
        html += f'<h{heading_value + 1}>{opening_tags_html}{p_html}{closing_tags_html}</h{heading_value + 1}>'
    elif target_block == 'ul':
        if not open_block:
            html += '<ul>'
            open_block = 'ul'
        html += f'<li>{opening_tags_html}{p_html}{closing_tags_html}</li>'
    elif target_block == 'callout':
        sticky_anchor = p_context.get('sticky_until') or (p_context.get('state', {}).get('callout_sticky_until') if p_context else None)
        if sticky_anchor and state and state.get('sticky_materials') is not None:
            state['sticky_materials'].append({
                'anchor': sticky_anchor,
                'p_index': p_index,
                'snippet': cleaned_p_text[:60]
            })
        if not open_block:
            sticky_attr = f' data-sticky-until="{sticky_anchor}"' if sticky_anchor else ''
            html += f'<div class="bs-callout bs-callout-info bs-callout-transcript"{sticky_attr}>'
            open_block = 'callout'
        else:
            if sticky_anchor:
                callout_idx = html.rfind('<div class="bs-callout')
                if callout_idx != -1:
                    tag_end = html.find('>', callout_idx)
                    open_tag = html[callout_idx:tag_end + 1]
                    if 'data-sticky-until' not in open_tag:
                        html = html[:tag_end] + f' data-sticky-until="{sticky_anchor}"' + html[tag_end:]
        html += f'<p>{opening_tags_html}{p_html}{closing_tags_html}</p>'
    elif target_block == 'blockquote':
        if not open_block:
            html += '<blockquote class="font-italic pl-4">'
            open_block = 'blockquote'
        html += f'<p>{opening_tags_html}{p_html}{closing_tags_html}</p>'
    else:
        sticky_anchor = p_context.get('sticky_until') if p_context else None
        if sticky_anchor and state and state.get('sticky_materials') is not None:
            state['sticky_materials'].append({
                'anchor': sticky_anchor,
                'p_index': p_index,
                'snippet': cleaned_p_text[:60]
            })
            if '[HTML]' in p_html:
                p_html = p_html.replace('[HTML]', f'[HTML data-sticky-until="{sticky_anchor}"]', 1)
            else:
                opening_tags_html = f'<div data-sticky-until="{sticky_anchor}">' + opening_tags_html
                closing_tags_html = closing_tags_html + '</div>'
        html += f'<p>{opening_tags_html}{p_html}{closing_tags_html}</p>'
    lines_map += p_map
    return html, lines_map, opened_tags, open_block

def get_bookmark_name_id(e):
    e_id = e.get(qn('w:id')) or (e.xpath('./@w:id')[0] if e.xpath('./@w:id') else None)
    e_name = e.get(qn('w:name')) or (e.xpath('./@w:name')[0] if e.xpath('./@w:name') else None)
    if e_name:
        e_name = unescape(e_name)
    return e_name, e_id

def get_run_style(run_obj: Run):
    font = getattr(run_obj, 'font', None)
    return {
        'italic': run_obj.italic,
        'bold': run_obj.bold,
        'underline': run_obj.underline,
        'strikethrough': getattr(font, 'strike', None) if font else None,
        'is_hyperlink': getattr(run_obj, 'is_hyperlink', False),
        'is_superscript': getattr(font, 'superscript', None) if font else None,
        'is_subscript': getattr(font, 'subscript', None) if font else None,
    }

def xml_parse_through_element(document:Document, runs_iterator, element,
                              html:str, transcript_map:list, opened_tags, current_style=None,
                              p_context=None):
    for sub in element.xpath('./*'):
        sub_name = sub.xpath('name()')
        if sub_name == 'w:t':
            text_nodes = sub.xpath('text()')
            t_text = text_nodes[0] if text_nodes else ''
            t_text = ZERO_WIDTH_CHARS_RE.sub('', t_text)
            if not t_text:
                continue
            if p_context and p_context.get('current_replica_entry') is not None:
                p_context['current_replica_entry']['text'] += t_text
            t_html = html_escape(t_text)
            if current_style['bold']:
                t_html = f'<strong>{t_html}</strong>'
            if current_style['italic']:
                t_html = f'<em>{t_html}</em>'
            if current_style['strikethrough']:
                t_html = f'<s>{t_html}</s>'
            if current_style['underline']:
                t_html = f'<u>{t_html}</u>'
            if current_style['is_superscript']:
                t_html = f'<sup>{t_html}</sup>'
            if current_style['is_subscript']:
                t_html = f'<sub>{t_html}</sub>'
            html += t_html
        elif sub_name == 'w:r':
            current_run:Run = next(runs_iterator)
            current_style = get_run_style(current_run)
            html, transcript_map, opened_tags = xml_parse_through_element(
                document, runs_iterator, sub, html,
                transcript_map, opened_tags, current_style,
                p_context=p_context
            )
        elif sub_name == 'w:hyperlink':
            anchor_attrs = sub.xpath('./@*[local-name()="anchor"]')
            if anchor_attrs and p_context:
                anchor_name = anchor_attrs[0]
                p_context['sticky_until'] = anchor_name
                state = p_context.get('state', {})
                state['callout_sticky_until'] = anchor_name

            for h_child in sub.xpath('./*'):
                h_name = h_child.xpath('name()')
                if h_name == 'w:r':
                    h_run = Run(h_child, None)
                    h_style = get_run_style(h_run)
                    html, transcript_map, opened_tags = xml_parse_through_element(
                        document, runs_iterator, h_child, html,
                        transcript_map, opened_tags, h_style,
                        p_context=p_context
                    )
                else:
                    html, transcript_map, opened_tags = xml_parse_through_element(
                        document, runs_iterator, h_child, html,
                        transcript_map, opened_tags, current_style,
                        p_context=p_context
                    )
        elif sub_name == 'w:bookmarkStart':
            bookmark_name, bookmark_id = get_bookmark_name_id(sub)
            if bookmark_name != '_GoBack':
                html += f'<span id="{bookmark_name}">'
                if p_context:
                    state = p_context.get('state', {})
                    if bookmark_name not in state.setdefault('active_bookmarks', []):
                        state['active_bookmarks'].append(bookmark_name)
                    if bookmark_name not in state.setdefault('pending_bookmarks', []):
                        state['pending_bookmarks'].append(bookmark_name)
                    curr = p_context.get('current_replica_entry')
                    if curr is not None:
                        if bookmark_name not in curr['bookmarks']:
                            curr['bookmarks'].append(bookmark_name)
                        if not curr.get('bookmark'):
                            curr['bookmark'] = bookmark_name
            opened_tags.append({'name': 'span', 'attrs': {'id': bookmark_name}})
        elif sub_name == 'w:bookmarkEnd':
            if opened_tags:
                tag = opened_tags[-1]
                b_name = tag.get('attrs', {}).get('id')
                if b_name != '_GoBack':
                    html += '</span>'
                    if p_context:
                        state = p_context.get('state', {})
                        active = state.get('active_bookmarks', [])
                        if b_name in active:
                            active.remove(b_name)
                if tag.get('name') == 'span':
                    opened_tags.pop(-1)
                else:
                    logger.warning('CAN NOT CLOSE TAG: SPAN')
        elif sub_name == 'w:commentRangeStart':
            comment_text = "".join(document.comments_part._element.get_comment_by_id(
                    int(sub.xpath('./@w:id')[0])).xpath('.//w:t/text()'))
            try:
                tokens = comment_text.strip().split(' ')
                l_id = None
                if len(tokens) >= 4 and tokens[-1].startswith('line'):
                    l_id = tokens[-1]
                    mm_end = tokens[-2]
                    mm_start = tokens[-3]
                    speaker = " ".join(tokens[:-3]).strip()
                else:
                    speaker, mm_start, mm_end = comment_text.rsplit(' ', 2)
                    speaker = speaker.strip()

                if p_context:
                    state = p_context.get('state', {})
                    last_speaker = state.get('last_speaker')
                    starts_with_dash = p_context.get('starts_with_dash')

                    if p_context.get('paragraph_speaker') is None:
                        if starts_with_dash:
                            if last_speaker is not None and speaker == last_speaker:
                                p_context['paragraph_speaker'] = 'unknown'
                            else:
                                p_context['paragraph_speaker'] = speaker
                        else:
                            if last_speaker is not None:
                                p_context['paragraph_speaker'] = last_speaker
                            else:
                                p_context['paragraph_speaker'] = speaker

                    effective_speaker = p_context['paragraph_speaker']
                    state['last_speaker'] = effective_speaker
                else:
                    effective_speaker = speaker

                # Collect bookmarks
                entry_bookmarks = []
                if p_context:
                    state = p_context.get('state', {})
                    for b in state.get('active_bookmarks', []):
                        if b not in entry_bookmarks:
                            entry_bookmarks.append(b)
                    for b in state.get('pending_bookmarks', []):
                        if b not in entry_bookmarks:
                            entry_bookmarks.append(b)
                    state['pending_bookmarks'] = []

                primary_bookmark = entry_bookmarks[0] if entry_bookmarks else None

                id_name = f"{effective_speaker}{mm_start}{mm_end}"
                line_id = l_id if l_id else f'line-{shortuuid.uuid(name=id_name)}'

                entry = {
                    'start': mm_start,
                    'end': mm_end,
                    'id': line_id,
                    'speaker': effective_speaker,
                    'text': '',
                    'bookmark': primary_bookmark,
                    'bookmarks': entry_bookmarks,
                }
                if p_context:
                    p_context['current_replica_entry'] = entry
                    if 'state' in p_context:
                        p_context['state']['active_replica_entry'] = entry
                transcript_map.append(entry)

                html += f'<span class="transcript-line" id="{line_id}" data-start="{mm_start}" data-end="{mm_end}" data-speaker="{effective_speaker}">'
                opened_tags.append({'name':'span', 'attrs':{
                    'class':'transcript-line',
                    'id':line_id,
                    'data-start': mm_start,
                    'data-end': mm_end,
                    'data-speaker': effective_speaker
                }})
            except ValueError:
                logger.warning('Wrong Comment: %s', comment_text)
                # Open a span to balance the </span> emitted on commentRangeEnd;
                html += '<span class="comment">'
                opened_tags.append({'name': 'span', 'attrs': {'class': 'comment'}})
        elif sub_name == 'w:commentRangeEnd':
            if p_context:
                p_context['current_replica_entry'] = None
                if 'state' in p_context:
                    p_context['state']['active_replica_entry'] = None
            html += '</span>'
            if opened_tags and opened_tags[-1]['name'] == 'span':
                opened_tags.pop(-1)
            else:
                logger.warning('CAN NOT CLOSE: SPAN')
        elif sub_name == 'w:br':
            html += '<br/>'
        elif sub_name == 'w:instrText':
            # TODO parse instrText
            ...
    return html, transcript_map, opened_tags

def get_html_and_map_from_docx(docx_file):
    document = Document(docx_file)
    # paragraph: Paragraph
    # run: Run
    # start_ends_map = []
    # html = ""
    # c = 0
    # for paragraph in document.paragraphs:
    #     html += "<p>"
    #     # iterating through every xml element inside paragraph
    #     for elem in paragraph._element.xpath('./*'):
    #         c += 1
    #         if elem.xpath('name()') == 'w:commentRangeStart':
    #             try:
    #                 speaker, mm_start, mm_end = "".join(document.comments_part._element.get_comment_by_id(
    #                     int(elem.xpath('./@w:id')[0])).xpath('.//w:t/text()')).split(' ')[:3]
    #             except ValueError as e:
    #                 print("".join(document.comments_part._element.get_comment_by_id(
    #                     int(elem.xpath('./@w:id')[0])).xpath('.//w:t/text()')))
    #             start_ends_map.append({'start':mm_start, 'end':mm_end, 'id':f'line{c}'})
    #             html += f'<span class="transcript-line" id="line{c}" data-start="{mm_start}" data-end="{mm_end}">'
    #         elif elem.xpath('name()') == 'w:r':
    #             for r_elem in elem.xpath('./*'):
    #                 c += 1
    #                 if r_elem.xpath('name()') == 'w:commentRangeStart':
    #                     speaker, mm_start, mm_end = document.comments_part._element.get_comment_by_id(
    #                         int(r_elem.xpath('./@w:id')[0])).xpath('.//w:t/text()')[0].split(' ')[:3]
    #                     start_ends_map.append({'start': mm_start, 'end': mm_end, 'id': f'line{c}'})
    #                     html += f'<span class="transcript-line" id="line{c}" data-start="{mm_start}" data-end="{mm_end}">'
    #                 elif r_elem.xpath('name()') == 'w:commentRangeEnd':
    #                     html += f'</span>'
    #                 elif r_elem.xpath('name()') == 'w:instrText':
    #                     # TODO: INCLUDE PICTURE OR LINK OR WHATEVER
    #                     pass
    #                 else:
    #                     html += f'{"".join(r_elem.xpath(".//text()"))}'
    #         elif elem.xpath('name()') == 'w:commentRangeEnd':
    #             html += f'</span>'
    #     html += '</p>'
    # html = re.sub('!\[(.+?)\]\((.+?)\s"(.+?)"\)', '<img title="\g<1>" src="\g<2>" alt="\g<3>">', html)
    return docx_parse_document(document)

def parse_toc_file(file):
    headings = []
    for line in file.lines():
        text, value = line.split('\t')
        headings.append((text, value))
    return headings

def set_headings(html, headings:List[Tuple[str, int]]):
    for line, h_value in headings:
        html = html.replace(f'<p>{line}</p>', f'<h{h_value}>{line}</h{h_value}>')
    return html

def parse_tags_file(file:TextIOWrapper):
    file.seek(0)
    styles = []
    for line in file.readlines():
        text, start_tag, end_tag = line.strip('\n').split('\t')
        styles.append((text, start_tag, end_tag))
    return styles

def set_tags(html, tags):
    for text, start_tag, end_tag in tags:
        html = html.replace(text, f'{start_tag}{text}{end_tag}')
    return html

def parse_docx(docx_file:BytesIO):
    document = Document(docx_file)
    starts_lines_map = {}
    start_ends_map = []
    html = ''
    inside_comment = True
    for paragraph in document.paragraphs:
        for elem in paragraph._element.xpath('./*'):
            if elem.xpath('name()') == 'w:commentRangeStart':
                speaker, mm_start, mm_end, l_id = document.comments_part._element.get_comment_by_id(
                    int(elem.xpath('./@w:id')[0])).xpath('.//w:t/text()')[0].split(' ')
                inside_comment = True
            elif elem.xpath('name()') == 'w:r':
                for r_elem in elem.xpath('./*'):
                    if r_elem.xpath('name()') == 'w:commentRangeStart':
                        speaker, mm_start, mm_end, l_id = document.comments_part._element.get_comment_by_id(
                            int(r_elem.xpath('./@w:id')[0])).xpath('.//w:t/text()')[0].split(' ')
                        inside_comment = True
                    elif r_elem.xpath('name()') == 'w:commentRangeEnd':
                        inside_comment = False
                    elif r_elem.xpath('name()') == 'w:instrText':
                        # TODO: INCLUDE PICTURE
                        pass
                    else:
                        if inside_comment:
                            ...
                        else:
                            ...
            elif elem.xpath('name()') == 'w:commentRangeEnd':
                inside_comment = False
        html += '</p>'
    html = re.sub('!\[(.+?)\]\((.+?)\s"(.+?)"\)', '<img title="\g<1>" src="\g<2>" alt="\g<3>">', html)
    return html, start_ends_map


def text_preprocessor(text:str):
    new_text = text.replace('--', '—')\
        .replace(' ?', ' ?')\
        .replace(' !', ' !')\
        .replace(' -', ' ‑')\
        .replace('- ', '— ')\
        .replace('...', '…')\
        .replace('[ ', '[').replace(' ]', ']')\
        .replace(' .', '.').replace(' ,', ',')
    #.replace('..', '…')\
    # new_text = re.sub('—(\w)', '— \g<1>', new_text)
    # new_text = re.sub('(\w)—', '\g<1> —', new_text)
    new_text = re.sub(r"([A-Za-zÀ-ÿ])'([A-Za-zÀ-ÿ])", r"\g<1>+++\g<2>", new_text)
    new_text = re.sub(r"\'", '"', new_text)
    new_text = re.sub(r"\+\+\+", "'", new_text)
    new_text = re.sub(r'"([\w\d\-])', r'«\g<1>', new_text)
    new_text = re.sub(r'([\w\d\-]|…|\.|!|\?)"', r'\g<1>»', new_text)
    new_text = re.sub(r'«\s', '« ', new_text)
    new_text = re.sub(r'\s»', ' »', new_text)
    new_text = re.sub(r'(\S)\(', r'\g<1> (', new_text)
    return new_text.lstrip(' ')


def parse_eaf(eaf_file:BinaryIO, sort_by_speaker) -> List[Dict]:
    eaf_file.seek(0)
    root = etree.parse(eaf_file)
    time_slots = {}
    for time_slot in root.xpath('./TIME_ORDER/TIME_SLOT'):
        time_slots[time_slot.xpath('@TIME_SLOT_ID')[0]] = int(time_slot.xpath('@TIME_VALUE')[0])
    transcript = []
    for tier in root.xpath('./TIER'):
        tier_id = str(tier.xpath('@TIER_ID')[0])
        for alignable_annotation in tier.xpath('.//ALIGNABLE_ANNOTATION'):
            time_start = time_slots[alignable_annotation.xpath('@TIME_SLOT_REF1')[0]]
            time_end = time_slots[alignable_annotation.xpath('@TIME_SLOT_REF2')[0]]
            texts = alignable_annotation.xpath('./ANNOTATION_VALUE/text()')
            if len(texts):
                text = "".join(texts)
            else:
                text = ""
            text = text_preprocessor(text)
            transcript.append({
                'speaker':tier_id,
                'start':time_start,
                'end':time_end,
                'text':text,
            })
    if sort_by_speaker:
        transcript.sort(key=lambda x: (x['speaker'], x['start']))
    else:
        transcript.sort(key=lambda x: x['start'])
    return transcript

def eaf_string_to_docx(s:str):
    if '\\\\' in s:
        r_pattern = re.compile(f"(?P<pre>.+)\\\\(?P<line>.+)\\\\(?P<post>.+)")
        match = re.search(r_pattern, s)
        pre_line, line, post_line = match.group('pre'), match.group('line'), match.group('post')
    else:
        pre_line, line, post_line = '', s, ''
    pre_line = pre_line.replace(r'\n', '\n')
    post_line = post_line.replace(r'\n', '\n')
    return pre_line, line, post_line

def map_to_docx(transcript_map, separate_speakers=True):
    document = docx.Document()
    last_speaker = None
    bookmark_id = 1
    current_p = None
    if not separate_speakers:
        current_p = document.add_paragraph('')
    for entry in transcript_map:
        speaker, start, end, text = entry['speaker'], entry['start'], entry['end'], entry['text']
        starts_with_numbered_list = bool(re.match(r'^\d+\)', text.strip()))
        if current_p is None or (separate_speakers and speaker != last_speaker):
            current_p = document.add_paragraph('— ')
        elif starts_with_numbered_list:
            current_p = document.add_paragraph('')
        else:
            pre_line, line_text, post_line = eaf_string_to_docx(text)
            current_p.add_run(' ')

        bookmarks = entry.get('bookmarks') or ([] if not entry.get('bookmark') else [entry['bookmark']])
        opened_bms = []
        for b_name in bookmarks:
            b_start = OxmlElement('w:bookmarkStart')
            b_start.set(qn('w:id'), str(bookmark_id))
            b_start.set(qn('w:name'), str(b_name))
            current_p._p.append(b_start)
            opened_bms.append(bookmark_id)
            bookmark_id += 1

        clean_run_text = PARAGRAPH_DIALOGUE_DASH_RE.sub('', text)
        clean_run_text = clean_run_text.replace('||', '').strip()
        anchored_text = clean_run_text if clean_run_text.startswith(ZERO_WIDTH_SPACE) else f'{ZERO_WIDTH_SPACE}{clean_run_text}'
        new_run = current_p.add_run(anchored_text)
        new_run.add_comment(f'{speaker} {start} {end}')

        for b_id in opened_bms:
            b_end = OxmlElement('w:bookmarkEnd')
            b_end.set(qn('w:id'), str(b_id))
            current_p._p.append(b_end)

        last_speaker = speaker
    file = BytesIO()
    document.save(file)
    file.seek(0)
    return file


def parse_ass_time(time_str):
    parts = time_str.strip().split(':')
    h = int(parts[0])
    m = int(parts[1])
    s_parts = parts[2].split('.')
    s = int(s_parts[0])
    if len(s_parts) > 1:
        fraction_str = s_parts[1].ljust(3, '0')[:3]
        ms = int(fraction_str)
    else:
        ms = 0
    return (h * 3600 + m * 60 + s) * 1000 + ms


def ms_to_ass_time(ms_val):
    if isinstance(ms_val, str):
        ms_val = int(ms_val)
    total_cs = int(round(ms_val / 10.0))
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def clean_ass_text(text):
    text = re.sub(r'\{.*?\}', '', text)
    text = text.replace(r'\N', ' ').replace(r'\n', ' ').replace(r'\h', ' ')
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = text.replace('||', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text_preprocessor(text)
    return text.strip()


def ass_to_map(ass_content_or_path):
    if hasattr(ass_content_or_path, 'read'):
        content = ass_content_or_path.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        lines = content.splitlines()
    elif isinstance(ass_content_or_path, str) and os.path.exists(ass_content_or_path):
        with open(ass_content_or_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    elif isinstance(ass_content_or_path, str):
        lines = ass_content_or_path.splitlines()
    else:
        raise ValueError('Unsupported input type for ass_to_map')

    transcript_map = []
    pending_bookmark = None

    for line in lines:
        line = line.strip()
        if line.startswith('Comment:'):
            match = re.search(r'===\s*BOOKMARK:\s*(.*?)\s*===', line)
            if match:
                pending_bookmark = match.group(1).strip()
            continue

        if not line.startswith('Dialogue:'):
            continue

        payload = line[len('Dialogue:'):].strip()
        parts = payload.split(',', 9)
        if len(parts) < 10:
            continue

        start_ms = parse_ass_time(parts[1])
        end_ms = parse_ass_time(parts[2])
        style = parts[3].strip()
        actor = parts[4].strip()
        effect = parts[8].strip()
        raw_text = parts[9]
        clean_text = clean_ass_text(raw_text)

        # Determine speaker: prioritize Actor (Subtitle Edit column), then style
        if actor:
            speaker = actor
        elif style and style not in ['Default', 'Split', 'Bookmark'] and not style.endswith('_Split'):
            speaker = style
        elif style.endswith('_Split'):
            speaker = style[:-6]
        else:
            speaker = 'unknown'

        # Determine bookmark
        bm_name = None
        if 'BOOKMARK:' in effect:
            bm_match = re.search(r'BOOKMARK:([^;]+)', effect)
            if bm_match:
                bm_name = bm_match.group(1).strip()
        elif pending_bookmark:
            bm_name = pending_bookmark
            pending_bookmark = None

        item = {
            'id': f"line-{len(transcript_map) + 1}",
            'speaker': speaker,
            'start': str(start_ms),
            'end': str(end_ms),
            'text': clean_text,
            'bookmark': bm_name,
            'bookmarks': [bm_name] if bm_name else [],
        }
        transcript_map.append(item)

    return transcript_map


def ass_to_docx(ass_content_or_path, separate_speakers=True):
    t_map = ass_to_map(ass_content_or_path)
    return map_to_docx(t_map, separate_speakers=separate_speakers)


def eaf_to_docx(eaf_file:BinaryIO, separate_speakers=True, sort_by_speaker=False):
    transcript_map = parse_eaf(eaf_file, sort_by_speaker)
    return map_to_docx(transcript_map, separate_speakers)

def map_to_eaf(map:List[Dict], eaf_file:BytesIO):
    eaf_file.seek(0)
    root = etree.parse(eaf_file)
    map_tiers = list(set([l['speaker'] for l in map]))
    eaf_tiers = root.xpath('./TIER/@TIER_ID')
    # checking that all tiers from map are present in given eaf file
    if not set(map_tiers).issubset(set(eaf_tiers)):
        raise ValueError('Not all tiers are present in given eaf file')
    # creating time_slots to speaker annotations relating map
    eaf_annotations = []
    for annotation in root.xpath('./TIER/ANNOTATION/ALIGNABLE_ANNOTATION/.'):
        start_time_id = annotation.xpath('@TIME_SLOT_REF1')[0]
        stop_time_id = annotation.xpath('@TIME_SLOT_REF2')[0]
        eaf_annotations.append({
            'id': annotation.xpath('@ANNOTATION_ID')[0],
            'start':root.xpath(f'./TIME_ORDER/TIME_SLOT[@TIME_SLOT_ID={start_time_id}]/@TIME_VALUE')[0],
            'end':root.xpath(f'./TIME_ORDER/TIME_SLOT[@TIME_SLOT_ID={stop_time_id}]/@TIME_VALUE')[0],
            'line':annotation.xpath('./ANNOTATION_VALUE/text()')[0],
        })
    # deleting time order slots
    root.remove(root.xpath('../TIME_SLOT'))
    # deleting tiers
    for tier in map_tiers:
        ...
    # replace all tiers lines with new one
    # with кускуфештп related time order slots
    ...
    # inserting new time order slots
    ...
    # saving all changes to eaf file
    ...


def get_currency(request):
    if request.user.is_authenticated:
        country_code = request.user.country_code
    else:
        country_code = request.session['geoip']['country_code']
    if country_code in ['CA']:
        return 'cad'
    elif country_code in ['CH', 'LI']:
        return 'chf'
    elif country_code in ['UK']:
        return 'gbp'
    elif country_code in EU_COUNTRIES:
        return 'eur'
    elif country_code in ['US']:
        return 'usd'
    elif country_code in ['IL']:
        return 'ils'
    elif country_code in ['RU', 'BY']:
        return 'rub'
    else:
        return 'eur'
