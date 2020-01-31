from collections import defaultdict
import binascii
from hashlib import md5

from django.conf import settings


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

