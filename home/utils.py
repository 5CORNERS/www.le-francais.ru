from collections import defaultdict
import binascii
from hashlib import md5
from io import BytesIO, StringIO

import docx
from docx import Document
from django.conf import settings
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from markdown import Markdown

from home.consts import COLUMN_TEXT, COLUMN_START, COLUMN_END, COLUMN_SPEAKER


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
     width="{width}" height="{height}">
  <rect width="{width}" height="{height}" style="{style}"></rect>
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
    if isinstance(root.specific, PageWithSidebar) or isinstance(root.specific,
                                                                LessonPage) or isinstance(
        root.specific, ArticlePage):
        menu_title = root.specific.menu_title
        if not isinstance(menu_title, str):
            menu_title = menu_title.decode()
        if menu_title != '':
            page_object["text"] = menu_title
        if not root.specific.is_selectable:
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
        nav_items = get_navigation_object_from_page(root, current_page)["nodes"]
    return nav_items

def parse_tab_delimited_srt_file(file):
    from csv import DictReader, excel_tab
    from collections import OrderedDict
    result = OrderedDict()
    c = 0
    for row in DictReader(file, dialect=excel_tab):
        result[row[COLUMN_TEXT]] = {
            "id": f'line{c}',
            "start":row[COLUMN_START],
            "end":row[COLUMN_END],
            "speaker":row[COLUMN_SPEAKER]
        }
        c += 1
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
    for l, data in parsed_table.items():
        speaker = data['speaker']
        if speaker != last_speaker:
            current_p:Paragraph = document.add_paragraph('— ')
        else:
            current_p.add_run(' ')
        new_run:Run = current_p.add_run(f'{l}')
        comment = new_run.add_comment(
            text=f'{data["speaker"]} {data["start"]} {data["end"]} {data["id"]}'
        )
        last_speaker = speaker
    file = BytesIO()
    document.save(file)
    return file


def get_html_and_map_from_docx(docx_file):
    document = Document(docx_file)
    paragraph: Paragraph
    run: Run
    start_ends_map = []
    html = ""
    for paragraph in document.paragraphs:
        html += "<p>"
        for elem in paragraph._element.xpath('./*'):
            if elem.xpath('name()') == 'w:commentRangeStart':
                speaker, mm_start, mm_end, l_id = document.comments_part._element.get_comment_by_id(
                    int(elem.xpath('./@w:id')[0])).xpath('.//w:t/text()')[0].split(' ')
                start_ends_map.append({'start':mm_start, 'end':mm_end, 'id':l_id})
                html += f'<span class="transcript-line" id="{l_id}" data-start="{mm_start}" data-end="{mm_end}">'
            elif elem.xpath('name()') == 'w:r':
                for r_elem in elem.xpath('./*'):
                    if r_elem.xpath('name()') == 'w:commentRangeStart':
                        speaker, mm_start, mm_end, l_id = document.comments_part._element.get_comment_by_id(
                            int(r_elem.xpath('./@w:id')[0])).xpath('.//w:t/text()')[0].split(' ')
                        start_ends_map.append({'start': mm_start, 'end': mm_end, 'id': l_id})
                        html += f'<span class="transcript-line" id="{l_id}" data-start="{mm_start}" data-end="{mm_end}">'
                    elif r_elem.xpath('name()') == 'w:commentRangeEnd':
                        html += f'</span>'
                    elif r_elem.xpath('name()') == 'w:instrText':
                        # TODO: INCLUDE PICTURE
                        pass
                    else:
                        html += f'{"".join(r_elem.xpath(".//text()"))}'
            elif elem.xpath('name()') == 'w:commentRangeEnd':
                html += f'</span>'
        html += '</p>'
    html = re.sub('!\[(.+?)\]\((.+?)\s"(.+?)"\)', '<img title="\g<1>" src="\g<2>" alt="\g<3>">', html)
    return html, start_ends_map

