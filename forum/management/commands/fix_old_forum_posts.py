import re

import pypandoc
from django.core.management import BaseCommand
from pybb.models import Category, Post

from custom_user.models import User

NAME2CODE_POINT = {
	r'AElig': 0x00c6,  # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1
	r'Aacute': 0x00c1,  # latin capital letter A with acute, U+00C1 ISOlat1
	r'Acirc': 0x00c2,  # latin capital letter A with circumflex, U+00C2 ISOlat1
	r'Agrave': 0x00c0,  # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1
	r'Alpha': 0x0391,  # greek capital letter alpha, U+0391
	r'Aring': 0x00c5,  # latin capital letter A with ring above = latin capital letter A ring, U+00C5 ISOlat1
	r'Atilde': 0x00c3,  # latin capital letter A with tilde, U+00C3 ISOlat1
	r'Auml': 0x00c4,  # latin capital letter A with diaeresis, U+00C4 ISOlat1
	r'Beta': 0x0392,  # greek capital letter beta, U+0392
	r'Ccedil': 0x00c7,  # latin capital letter C with cedilla, U+00C7 ISOlat1
	r'Chi': 0x03a7,  # greek capital letter chi, U+03A7
	r'Dagger': 0x2021,  # double dagger, U+2021 ISOpub
	r'Delta': 0x0394,  # greek capital letter delta, U+0394 ISOgrk3
	r'ETH': 0x00d0,  # latin capital letter ETH, U+00D0 ISOlat1
	r'Eacute': 0x00c9,  # latin capital letter E with acute, U+00C9 ISOlat1
	r'Ecirc': 0x00ca,  # latin capital letter E with circumflex, U+00CA ISOlat1
	r'Egrave': 0x00c8,  # latin capital letter E with grave, U+00C8 ISOlat1
	r'Epsilon': 0x0395,  # greek capital letter epsilon, U+0395
	r'Eta': 0x0397,  # greek capital letter eta, U+0397
	r'Euml': 0x00cb,  # latin capital letter E with diaeresis, U+00CB ISOlat1
	r'Gamma': 0x0393,  # greek capital letter gamma, U+0393 ISOgrk3
	r'Iacute': 0x00cd,  # latin capital letter I with acute, U+00CD ISOlat1
	r'Icirc': 0x00ce,  # latin capital letter I with circumflex, U+00CE ISOlat1
	r'Igrave': 0x00cc,  # latin capital letter I with grave, U+00CC ISOlat1
	r'Iota': 0x0399,  # greek capital letter iota, U+0399
	r'Iuml': 0x00cf,  # latin capital letter I with diaeresis, U+00CF ISOlat1
	r'Kappa': 0x039a,  # greek capital letter kappa, U+039A
	r'Lambda': 0x039b,  # greek capital letter lambda, U+039B ISOgrk3
	r'Mu': 0x039c,  # greek capital letter mu, U+039C
	r'Ntilde': 0x00d1,  # latin capital letter N with tilde, U+00D1 ISOlat1
	r'Nu': 0x039d,  # greek capital letter nu, U+039D
	r'OElig': 0x0152,  # latin capital ligature OE, U+0152 ISOlat2
	r'Oacute': 0x00d3,  # latin capital letter O with acute, U+00D3 ISOlat1
	r'Ocirc': 0x00d4,  # latin capital letter O with circumflex, U+00D4 ISOlat1
	r'Ograve': 0x00d2,  # latin capital letter O with grave, U+00D2 ISOlat1
	r'Omega': 0x03a9,  # greek capital letter omega, U+03A9 ISOgrk3
	r'Omicron': 0x039f,  # greek capital letter omicron, U+039F
	r'Oslash': 0x00d8,  # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1
	r'Otilde': 0x00d5,  # latin capital letter O with tilde, U+00D5 ISOlat1
	r'Ouml': 0x00d6,  # latin capital letter O with diaeresis, U+00D6 ISOlat1
	r'Phi': 0x03a6,  # greek capital letter phi, U+03A6 ISOgrk3
	r'Pi': 0x03a0,  # greek capital letter pi, U+03A0 ISOgrk3
	r'Prime': 0x2033,  # double prime = seconds = inches, U+2033 ISOtech
	r'Psi': 0x03a8,  # greek capital letter psi, U+03A8 ISOgrk3
	r'Rho': 0x03a1,  # greek capital letter rho, U+03A1
	r'Scaron': 0x0160,  # latin capital letter S with caron, U+0160 ISOlat2
	r'Sigma': 0x03a3,  # greek capital letter sigma, U+03A3 ISOgrk3
	r'THORN': 0x00de,  # latin capital letter THORN, U+00DE ISOlat1
	r'Tau': 0x03a4,  # greek capital letter tau, U+03A4
	r'Theta': 0x0398,  # greek capital letter theta, U+0398 ISOgrk3
	r'Uacute': 0x00da,  # latin capital letter U with acute, U+00DA ISOlat1
	r'Ucirc': 0x00db,  # latin capital letter U with circumflex, U+00DB ISOlat1
	r'Ugrave': 0x00d9,  # latin capital letter U with grave, U+00D9 ISOlat1
	r'Upsilon': 0x03a5,  # greek capital letter upsilon, U+03A5 ISOgrk3
	r'Uuml': 0x00dc,  # latin capital letter U with diaeresis, U+00DC ISOlat1
	r'Xi': 0x039e,  # greek capital letter xi, U+039E ISOgrk3
	r'Yacute': 0x00dd,  # latin capital letter Y with acute, U+00DD ISOlat1
	r'Yuml': 0x0178,  # latin capital letter Y with diaeresis, U+0178 ISOlat2
	r'Zeta': 0x0396,  # greek capital letter zeta, U+0396
	r'aacute': 0x00e1,  # latin small letter a with acute, U+00E1 ISOlat1
	r'acirc': 0x00e2,  # latin small letter a with circumflex, U+00E2 ISOlat1
	r'acute': 0x00b4,  # acute accent = spacing acute, U+00B4 ISOdia
	r'aelig': 0x00e6,  # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1
	r'agrave': 0x00e0,  # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1
	r'alefsym': 0x2135,  # alef symbol = first transfinite cardinal, U+2135 NEW
	r'alpha': 0x03b1,  # greek small letter alpha, U+03B1 ISOgrk3
	r'amp': 0x0026,  # ampersand, U+0026 ISOnum
	r'and': 0x2227,  # logical and = wedge, U+2227 ISOtech
	r'ang': 0x2220,  # angle, U+2220 ISOamso
	r'aring': 0x00e5,  # latin small letter a with ring above = latin small letter a ring, U+00E5 ISOlat1
	r'asymp': 0x2248,  # almost equal to = asymptotic to, U+2248 ISOamsr
	r'atilde': 0x00e3,  # latin small letter a with tilde, U+00E3 ISOlat1
	r'auml': 0x00e4,  # latin small letter a with diaeresis, U+00E4 ISOlat1
	r'bdquo': 0x201e,  # double low-9 quotation mark, U+201E NEW
	r'beta': 0x03b2,  # greek small letter beta, U+03B2 ISOgrk3
	r'brvbar': 0x00a6,  # broken bar = broken vertical bar, U+00A6 ISOnum
	r'bull': 0x2022,  # bullet = black small circle, U+2022 ISOpub
	r'cap': 0x2229,  # intersection = cap, U+2229 ISOtech
	r'ccedil': 0x00e7,  # latin small letter c with cedilla, U+00E7 ISOlat1
	r'cedil': 0x00b8,  # cedilla = spacing cedilla, U+00B8 ISOdia
	r'cent': 0x00a2,  # cent sign, U+00A2 ISOnum
	r'chi': 0x03c7,  # greek small letter chi, U+03C7 ISOgrk3
	r'circ': 0x02c6,  # modifier letter circumflex accent, U+02C6 ISOpub
	r'clubs': 0x2663,  # black club suit = shamrock, U+2663 ISOpub
	r'cong': 0x2245,  # approximately equal to, U+2245 ISOtech
	r'copy': 0x00a9,  # copyright sign, U+00A9 ISOnum
	r'crarr': 0x21b5,  # downwards arrow with corner leftwards = carriage return, U+21B5 NEW
	r'cup': 0x222a,  # union = cup, U+222A ISOtech
	r'curren': 0x00a4,  # currency sign, U+00A4 ISOnum
	r'dArr': 0x21d3,  # downwards double arrow, U+21D3 ISOamsa
	r'dagger': 0x2020,  # dagger, U+2020 ISOpub
	r'darr': 0x2193,  # downwards arrow, U+2193 ISOnum
	r'deg': 0x00b0,  # degree sign, U+00B0 ISOnum
	r'delta': 0x03b4,  # greek small letter delta, U+03B4 ISOgrk3
	r'diams': 0x2666,  # black diamond suit, U+2666 ISOpub
	r'divide': 0x00f7,  # division sign, U+00F7 ISOnum
	r'eacute': 0x00e9,  # latin small letter e with acute, U+00E9 ISOlat1
	r'ecirc': 0x00ea,  # latin small letter e with circumflex, U+00EA ISOlat1
	r'egrave': 0x00e8,  # latin small letter e with grave, U+00E8 ISOlat1
	r'empty': 0x2205,  # empty set = null set = diameter, U+2205 ISOamso
	r'emsp': 0x2003,  # em space, U+2003 ISOpub
	r'ensp': 0x2002,  # en space, U+2002 ISOpub
	r'epsilon': 0x03b5,  # greek small letter epsilon, U+03B5 ISOgrk3
	r'equiv': 0x2261,  # identical to, U+2261 ISOtech
	r'eta': 0x03b7,  # greek small letter eta, U+03B7 ISOgrk3
	r'eth': 0x00f0,  # latin small letter eth, U+00F0 ISOlat1
	r'euml': 0x00eb,  # latin small letter e with diaeresis, U+00EB ISOlat1
	r'euro': 0x20ac,  # euro sign, U+20AC NEW
	r'exist': 0x2203,  # there exists, U+2203 ISOtech
	r'fnof': 0x0192,  # latin small f with hook = function = florin, U+0192 ISOtech
	r'forall': 0x2200,  # for all, U+2200 ISOtech
	r'frac12': 0x00bd,  # vulgar fraction one half = fraction one half, U+00BD ISOnum
	r'frac14': 0x00bc,  # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum
	r'frac34': 0x00be,  # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum
	r'frasl': 0x2044,  # fraction slash, U+2044 NEW
	r'gamma': 0x03b3,  # greek small letter gamma, U+03B3 ISOgrk3
	r'ge': 0x2265,  # greater-than or equal to, U+2265 ISOtech
	r'gt': 0x003e,  # greater-than sign, U+003E ISOnum
	r'hArr': 0x21d4,  # left right double arrow, U+21D4 ISOamsa
	r'harr': 0x2194,  # left right arrow, U+2194 ISOamsa
	r'hearts': 0x2665,  # black heart suit = valentine, U+2665 ISOpub
	r'hellip': 0x2026,  # horizontal ellipsis = three dot leader, U+2026 ISOpub
	r'iacute': 0x00ed,  # latin small letter i with acute, U+00ED ISOlat1
	r'icirc': 0x00ee,  # latin small letter i with circumflex, U+00EE ISOlat1
	r'iexcl': 0x00a1,  # inverted exclamation mark, U+00A1 ISOnum
	r'igrave': 0x00ec,  # latin small letter i with grave, U+00EC ISOlat1
	r'image': 0x2111,  # blackletter capital I = imaginary part, U+2111 ISOamso
	r'infin': 0x221e,  # infinity, U+221E ISOtech
	r'int': 0x222b,  # integral, U+222B ISOtech
	r'iota': 0x03b9,  # greek small letter iota, U+03B9 ISOgrk3
	r'iquest': 0x00bf,  # inverted question mark = turned question mark, U+00BF ISOnum
	r'isin': 0x2208,  # element of, U+2208 ISOtech
	r'iuml': 0x00ef,  # latin small letter i with diaeresis, U+00EF ISOlat1
	r'kappa': 0x03ba,  # greek small letter kappa, U+03BA ISOgrk3
	r'lArr': 0x21d0,  # leftwards double arrow, U+21D0 ISOtech
	r'lambda': 0x03bb,  # greek small letter lambda, U+03BB ISOgrk3
	r'lang': 0x2329,  # left-pointing angle bracket = bra, U+2329 ISOtech
	r'laquo': 0x00ab,  # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum
	r'larr': 0x2190,  # leftwards arrow, U+2190 ISOnum
	r'lceil': 0x2308,  # left ceiling = apl upstile, U+2308 ISOamsc
	r'ldquo': 0x201c,  # left double quotation mark, U+201C ISOnum
	r'le': 0x2264,  # less-than or equal to, U+2264 ISOtech
	r'lfloor': 0x230a,  # left floor = apl downstile, U+230A ISOamsc
	r'lowast': 0x2217,  # asterisk operator, U+2217 ISOtech
	r'loz': 0x25ca,  # lozenge, U+25CA ISOpub
	r'lrm': 0x200e,  # left-to-right mark, U+200E NEW RFC 2070
	r'lsaquo': 0x2039,  # single left-pointing angle quotation mark, U+2039 ISO proposed
	r'lsquo': 0x2018,  # left single quotation mark, U+2018 ISOnum
	r'lt': 0x003c,  # less-than sign, U+003C ISOnum
	r'macr': 0x00af,  # macron = spacing macron = overline = APL overbar, U+00AF ISOdia
	r'mdash': 0x2014,  # em dash, U+2014 ISOpub
	r'micro': 0x00b5,  # micro sign, U+00B5 ISOnum
	r'middot': 0x00b7,  # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum
	r'minus': 0x2212,  # minus sign, U+2212 ISOtech
	r'mu': 0x03bc,  # greek small letter mu, U+03BC ISOgrk3
	r'nabla': 0x2207,  # nabla = backward difference, U+2207 ISOtech
	r'nbsp': 0x00a0,  # no-break space = non-breaking space, U+00A0 ISOnum
	r'ndash': 0x2013,  # en dash, U+2013 ISOpub
	r'ne': 0x2260,  # not equal to, U+2260 ISOtech
	r'ni': 0x220b,  # contains as member, U+220B ISOtech
	r'not': 0x00ac,  # not sign, U+00AC ISOnum
	r'notin': 0x2209,  # not an element of, U+2209 ISOtech
	r'nsub': 0x2284,  # not a subset of, U+2284 ISOamsn
	r'ntilde': 0x00f1,  # latin small letter n with tilde, U+00F1 ISOlat1
	r'nu': 0x03bd,  # greek small letter nu, U+03BD ISOgrk3
	r'oacute': 0x00f3,  # latin small letter o with acute, U+00F3 ISOlat1
	r'ocirc': 0x00f4,  # latin small letter o with circumflex, U+00F4 ISOlat1
	r'oelig': 0x0153,  # latin small ligature oe, U+0153 ISOlat2
	r'ograve': 0x00f2,  # latin small letter o with grave, U+00F2 ISOlat1
	r'oline': 0x203e,  # overline = spacing overscore, U+203E NEW
	r'omega': 0x03c9,  # greek small letter omega, U+03C9 ISOgrk3
	r'omicron': 0x03bf,  # greek small letter omicron, U+03BF NEW
	r'oplus': 0x2295,  # circled plus = direct sum, U+2295 ISOamsb
	r'or': 0x2228,  # logical or = vee, U+2228 ISOtech
	r'ordf': 0x00aa,  # feminine ordinal indicator, U+00AA ISOnum
	r'ordm': 0x00ba,  # masculine ordinal indicator, U+00BA ISOnum
	r'oslash': 0x00f8,  # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1
	r'otilde': 0x00f5,  # latin small letter o with tilde, U+00F5 ISOlat1
	r'otimes': 0x2297,  # circled times = vector product, U+2297 ISOamsb
	r'ouml': 0x00f6,  # latin small letter o with diaeresis, U+00F6 ISOlat1
	r'para': 0x00b6,  # pilcrow sign = paragraph sign, U+00B6 ISOnum
	r'part': 0x2202,  # partial differential, U+2202 ISOtech
	r'permil': 0x2030,  # per mille sign, U+2030 ISOtech
	r'perp': 0x22a5,  # up tack = orthogonal to = perpendicular, U+22A5 ISOtech
	r'phi': 0x03c6,  # greek small letter phi, U+03C6 ISOgrk3
	r'pi': 0x03c0,  # greek small letter pi, U+03C0 ISOgrk3
	r'piv': 0x03d6,  # greek pi symbol, U+03D6 ISOgrk3
	r'plusmn': 0x00b1,  # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum
	r'pound': 0x00a3,  # pound sign, U+00A3 ISOnum
	r'prime': 0x2032,  # prime = minutes = feet, U+2032 ISOtech
	r'prod': 0x220f,  # n-ary product = product sign, U+220F ISOamsb
	r'prop': 0x221d,  # proportional to, U+221D ISOtech
	r'psi': 0x03c8,  # greek small letter psi, U+03C8 ISOgrk3
	r'quot': 0x0022,  # quotation mark = APL quote, U+0022 ISOnum
	r'rArr': 0x21d2,  # rightwards double arrow, U+21D2 ISOtech
	r'radic': 0x221a,  # square root = radical sign, U+221A ISOtech
	r'rang': 0x232a,  # right-pointing angle bracket = ket, U+232A ISOtech
	r'raquo': 0x00bb,  # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum
	r'rarr': 0x2192,  # rightwards arrow, U+2192 ISOnum
	r'rceil': 0x2309,  # right ceiling, U+2309 ISOamsc
	r'rdquo': 0x201d,  # right double quotation mark, U+201D ISOnum
	r'real': 0x211c,  # blackletter capital R = real part symbol, U+211C ISOamso
	r'reg': 0x00ae,  # registered sign = registered trade mark sign, U+00AE ISOnum
	r'rfloor': 0x230b,  # right floor, U+230B ISOamsc
	r'rho': 0x03c1,  # greek small letter rho, U+03C1 ISOgrk3
	r'rlm': 0x200f,  # right-to-left mark, U+200F NEW RFC 2070
	r'rsaquo': 0x203a,  # single right-pointing angle quotation mark, U+203A ISO proposed
	r'rsquo': 0x2019,  # right single quotation mark, U+2019 ISOnum
	r'sbquo': 0x201a,  # single low-9 quotation mark, U+201A NEW
	r'scaron': 0x0161,  # latin small letter s with caron, U+0161 ISOlat2
	r'sdot': 0x22c5,  # dot operator, U+22C5 ISOamsb
	r'sect': 0x00a7,  # section sign, U+00A7 ISOnum
	r'shy': 0x00ad,  # soft hyphen = discretionary hyphen, U+00AD ISOnum
	r'sigma': 0x03c3,  # greek small letter sigma, U+03C3 ISOgrk3
	r'sigmaf': 0x03c2,  # greek small letter final sigma, U+03C2 ISOgrk3
	r'sim': 0x223c,  # tilde operator = varies with = similar to, U+223C ISOtech
	r'spades': 0x2660,  # black spade suit, U+2660 ISOpub
	r'sub': 0x2282,  # subset of, U+2282 ISOtech
	r'sube': 0x2286,  # subset of or equal to, U+2286 ISOtech
	r'sum': 0x2211,  # n-ary sumation, U+2211 ISOamsb
	r'sup': 0x2283,  # superset of, U+2283 ISOtech
	r'sup1': 0x00b9,  # superscript one = superscript digit one, U+00B9 ISOnum
	r'sup2': 0x00b2,  # superscript two = superscript digit two = squared, U+00B2 ISOnum
	r'sup3': 0x00b3,  # superscript three = superscript digit three = cubed, U+00B3 ISOnum
	r'supe': 0x2287,  # superset of or equal to, U+2287 ISOtech
	r'szlig': 0x00df,  # latin small letter sharp s = ess-zed, U+00DF ISOlat1
	r'tau': 0x03c4,  # greek small letter tau, U+03C4 ISOgrk3
	r'there4': 0x2234,  # therefore, U+2234 ISOtech
	r'theta': 0x03b8,  # greek small letter theta, U+03B8 ISOgrk3
	r'thetasym': 0x03d1,  # greek small letter theta symbol, U+03D1 NEW
	r'thinsp': 0x2009,  # thin space, U+2009 ISOpub
	r'thorn': 0x00fe,  # latin small letter thorn with, U+00FE ISOlat1
	r'tilde': 0x02dc,  # small tilde, U+02DC ISOdia
	r'times': 0x00d7,  # multiplication sign, U+00D7 ISOnum
	r'trade': 0x2122,  # trade mark sign, U+2122 ISOnum
	r'uArr': 0x21d1,  # upwards double arrow, U+21D1 ISOamsa
	r'uacute': 0x00fa,  # latin small letter u with acute, U+00FA ISOlat1
	r'uarr': 0x2191,  # upwards arrow, U+2191 ISOnum
	r'ucirc': 0x00fb,  # latin small letter u with circumflex, U+00FB ISOlat1
	r'ugrave': 0x00f9,  # latin small letter u with grave, U+00F9 ISOlat1
	r'uml': 0x00a8,  # diaeresis = spacing diaeresis, U+00A8 ISOdia
	r'upsih': 0x03d2,  # greek upsilon with hook symbol, U+03D2 NEW
	r'upsilon': 0x03c5,  # greek small letter upsilon, U+03C5 ISOgrk3
	r'uuml': 0x00fc,  # latin small letter u with diaeresis, U+00FC ISOlat1
	r'weierp': 0x2118,  # script capital P = power set = Weierstrass p, U+2118 ISOamso
	r'xi': 0x03be,  # greek small letter xi, U+03BE ISOgrk3
	r'yacute': 0x00fd,  # latin small letter y with acute, U+00FD ISOlat1
	r'yen': 0x00a5,  # yen sign = yuan sign, U+00A5 ISOnum
	r'yuml': 0x00ff,  # latin small letter y with diaeresis, U+00FF ISOlat1
	r'zeta': 0x03b6,  # greek small letter zeta, U+03B6 ISOgrk3
	r'zwj': 0x200d,  # zero width joiner, U+200D NEW RFC 2070
	r'zwnj': 0x200c,  # zero width non-joiner, U+200C NEW RFC 2070
}

RUS2FR_CHARS = {
	r'А': 'À',
	r'а': 'à',
	r'В': 'Â',
	r'в': 'â',
	r'З': 'Ç',
	r'з': 'ç',
	r'И': 'È',
	r'и': 'è',
	r'Й': 'É',
	r'й': 'é',
	r'К': 'Ê',
	r'к': 'ê',
	r'Л': 'Ë',
	r'л': 'ë',
	r'О': 'Î',
	r'о': 'î',
	r'П': 'Ï',
	r'п': 'ï',
	r'Ф': 'Ô',
	r'ф': 'ô',
	r'Щ': 'Ù',
	r'щ': 'ù',
	r'Ы': 'Û',
	r'ы': 'û',
	r'Ь': 'Ü',
	r'ь': 'ü',
	r'џ': 'Ÿ',
	r'я': 'ÿ',
	r'Ж': 'Æ',
	r'ж': 'æ',
	r'Њ': 'Œ',
	r'њ': 'œ',
}

UNICODE_ESCAPE = {
	'\\u0401': 'Ё',
	'\\u0410': 'А',
	'\\u0411': 'Б',
	'\\u0412': 'В',
	'\\u0413': 'Г',
	'\\u0414': 'Д',
	'\\u0415': 'Е',
	'\\u0416': 'Ж',
	'\\u0417': 'З',
	'\\u0418': 'И',
	'\\u0419': 'Й',
	'\\u041a': 'К',
	'\\u041b': 'Л',
	'\\u041c': 'М',
	'\\u041d': 'Н',
	'\\u041e': 'О',
	'\\u041f': 'П',
	'\\u0420': 'Р',
	'\\u0421': 'С',
	'\\u0422': 'Т',
	'\\u0423': 'У',
	'\\u0424': 'Ф',
	'\\u0425': 'Х',
	'\\u0426': 'Ц',
	'\\u0427': 'Ч',
	'\\u0428': 'Ш',
	'\\u0429': 'Щ',
	'\\u042a': 'Ъ',
	'\\u042b': 'Ы',
	'\\u042c': 'Ь',
	'\\u042d': 'Э',
	'\\u042e': 'Ю',
	'\\u042f': 'Я',
	'\\u0430': 'а',
	'\\u0431': 'б',
	'\\u0432': 'в',
	'\\u0433': 'г',
	'\\u0434': 'д',
	'\\u0435': 'е',
	'\\u0436': 'ж',
	'\\u0437': 'з',
	'\\u0438': 'и',
	'\\u0439': 'й',
	'\\u043a': 'к',
	'\\u043b': 'л',
	'\\u043c': 'м',
	'\\u043d': 'н',
	'\\u043e': 'о',
	'\\u043f': 'п',
	'\\u0440': 'р',
	'\\u0441': 'с',
	'\\u0442': 'т',
	'\\u0443': 'у',
	'\\u0444': 'ф',
	'\\u0445': 'х',
	'\\u0446': 'ц',
	'\\u0447': 'ч',
	'\\u0448': 'ш',
	'\\u0449': 'щ',
	'\\u044a': 'ъ',
	'\\u044b': 'ы',
	'\\u044c': 'ь',
	'\\u044d': 'э',
	'\\u044e': 'ю',
	'\\u044f': 'я',
	'\\u0451': 'ё',
	'\\u045d': 'ѝ',
	'\\u2026': '…',
	'\\u2014': '—',
	'\\u045f': 'џ',
	'\\u040a': 'Њ',
	'\\u045a': 'њ',
}

EMAIL_REGEX = r'([a-zA-Z0-9_.+-]+\@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'

LINE_WITH_EMAIL_REGEX = r'(^[^\n\r]*' + EMAIL_REGEX + r'[^\n\r]*)'

USERNAME_FROM_LINE = r'((\s|пользователь)([А-яA-Za-z0-9_\s])+(?=(\s<{0,1}[a-zA-Z0-9_.+-]+\@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+>{0,1})))'


class Table:
	post_lines_table = {}
	users_table = {}

	def __init__(self, category):
		for forum in category.forums.all():
			for topic in forum.topics.all():
				for post in topic.posts.all():
					self.build_table(post)

	def build_table(self, post):
		post_row = []
		for match in re.finditer(LINE_WITH_EMAIL_REGEX, post.body, flags=re.M):
			line_start, line_end = int(match.start()), int(match.end())
			line = post.body[line_start:line_end]
			email, email_start, email_end = get_substring(EMAIL_REGEX, line)
			raw_username = ''
			try:
				raw_username = re.search(USERNAME_FROM_LINE, line, flags=re.M | re.I).group(1)
				username = raw_username.replace('пользователь', '').replace(' от', '').strip()
			except:
				username = ''

			self.add_user(username, email)

			line_row = {'line': line, 'line_start': line_start, 'line_end': line_end, 'email': email,
			            'email_start': email_start, 'email_end': email_end, 'username': username,
			            'raw_username': raw_username}

			post_row.append(line_row)
		if post_row != []:
			self.post_lines_table[str(post.id)] = post_row

	def add_user(self, username, email):
		if username == '':
			try:
				username = User.objects.get(email=email).username
			except:
				pass
		if email in self.users_table.keys():
			if self.users_table[email][0] != '':
				self.users_table[email][0] = username
				self.users_table[email][1] += 1
		else:
			self.users_table[email] = [str(), int()]
			self.users_table[email][0] = username
			self.users_table[email][1] = 0

	def email_handler(self):
		for id, post_row in self.post_lines_table.items():
			for line_row in post_row:
				email = line_row['email']
				if self.users_table[line_row['email']][0] == '':  # Проверяем наличие username в сводной таблице пользователей
					line_row['email'] = hide_email(line_row['email'])  # Если нет скрываем email точками
				else:
					line_row['email'] = self.users_table[line_row['email']][0]  # Если есть заменяем email на username из таблицы

				if line_row['username'] == '':  # Проверяем наличее username в строке
					line_row['line'] = line_row['line'][:line_row['email_start']] + line_row['email'] \
					                   + line_row['line'][line_row['email_end']:]  # Если нет -- смело пишем новый "email"
				else:
					line_row['line'] = line_row['line'][:line_row['email_start']] \
					                   + line_row['line'][line_row['email_end']:]  # Если есть -- вырезаем email

				if not bool(re.search(r'^.*\s>.+$', line_row['line'])):  # Проверяем на шевроны в начале строки
					# Если их нет
					if not bool(re.search(r'^\?\?\?.+$', line_row['line'])):  # Проверяем на ???
						line_row['line'] = '\n???- \"' + line_row['line'] + '\"\n'  # Если нет добавляем ???

	def save_to_post(self):
		for id, post_row in self.post_lines_table.items():
			for line_row in reversed(post_row):
				line_start = line_row['line_start']
				line_end = line_row['line_end']
				post = Post.objects.get(id=id)
				post.body = post.body[:line_start] + line_row['line'] + post.body[line_end:]
				post.body = re.sub(r'\<\>', '', post.body)


class Command(BaseCommand):
	def handle(self, *args, **options):
		category = Category.objects.get(name="Old")
		# table = Table(category)
		# print('Table has been commpleted')
		# table.email_handler()
		# table.save_to_post()
		print_all_links(category)
		# find_wrong_details(category)


def get_substring(pattern, string):
	match_object = re.search(pattern, string)
	substring_start, substring_end = int(match_object.start()), int(match_object.end())
	substring = match_object.group(1)
	return substring, substring_start, substring_end

def find_wrong_details(category):
	pattern = r'(^(le|sur)\s.+?\n{0,1}.*?(écrit|йcrit)\s:)'
	for forum in category.forums.all():
		for topic in forum.topics.all():
			for post in topic.posts.all():
				post_rows = []
				for match in re.finditer(pattern, post.body, flags=re.I|re.M):
					line_start, line_end = int(match.start()), int(match.end())
					line = post.body[line_start:line_end]
					line = '???- "' + re.sub(r'\:$', '. . .', line) + '\"'
					post_row = (line_start, line_end, line)
					post_rows.append(post_row)
				if post_rows != []:
					for line in reversed(post_rows):
						post.body = post.body[:line[0]] + line[2] + post.body[line[1]:]
						post.save()

def print_all_links(category):
	for forum in category.forums.all():
		for topic in forum.topics.all():
			print('http://192.168.0.27:8000/forum/topic/' + str(
					topic.id) + '\t' + topic.name + '\t' + topic.forum.category.name +'\t' + str(topic.post_count))


def hide_email(email):
	username, username_start, username_end = get_substring(r'([a-zA-Z0-9_.+-]+(?=\@))', email)
	if bool(re.search(r'\.\.\.', username)):
		return email
	new_username = ''
	if len(username) > 3:
		for i in range(len(username)):
			if i >= 3:
				new_username += '#'
			else:
				new_username += username[i]
		return re.sub('\#+', '...', new_username) + email[username_end:]
	else:
		return '...' + email[username_end:]


def fix_post(post):
	post.body = text_decode(post.body)
	# post.body = spoiler_bloquote(post.body)
	post.body = del_phrases(post.body)
	pass


def text_decode(text):
	if re.search(r'\\u', text):
		body = fix_arnaud_post(text)
	elif is_html(text):
		text = escape_special_characters(text)
		body = pypandoc.convert_text(text, 'markdown_strict', format='html')
	else:
		body = text
	return body


def fix_arnaud_post(text):
	text = rus2fr(text)
	text = unicode_escape(text)
	return text


def rus2fr(text):
	for rus, fr in RUS2FR_CHARS.items():
		text = re.sub(rus, fr, text)
	return text


def unicode_escape(text):
	for u, rus in UNICODE_ESCAPE.items():
		text = text.replace(u, rus)
	return text


def is_utf(text):
	regex = re.compile(r'(\\\\u([a-z]|[0-9]){4})')
	return re.match(regex, text)


def is_html(text):
	return True if re.search(r'<(div|/div|a|b|p|i|blockquote)>', text) else False


def spoiler_bloquote(text):
	head_raw = r'(^(((le|sur)\s.*?\n{0,1}.*?(écrit|йcrit)\s:$)|(on\s.*?\n{0,1}.*?wrote:$)|((([0-9]{2}\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))|понедельник|вторник|среда|четверг|пятница|суббота|воскресенье).*?\n{0,1}.*?написал:$)|(El\s.*?\n{0,1}.*?escribió:$)|(201[0-7].*?\n{0,1}.*?(<*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+>*):{0,1}$)))'
	for head in re.finditer(
			head_raw,
			text, flags=(re.M | re.I)
	):
		s = int(head.start())
		e = int(head.end())
		text = text[:s] + text[s:e].replace('\n', ' ') + text[e:]
		text = text[:s] + text[s:e].replace('<', '') + text[e:]
		text = text[:s] + text[s:e].replace('>', '') + text[e:]
	text = re.sub(
		head_raw,
		'\n' + r'???- "\1"',
		text, flags=(re.M | re.I))
	text = re.sub(r'(^>)', ' ' * 4 + '>', text, flags=re.M)
	return text


def del_phrases(text: str):
	regex = r'''(^.*Вы получили это сообщение[\s\S]+?(optout|opt_out).)'''
	opt_out_regex = r'''\n<http.+?(opt_out|optout)>\.{0,1}'''
	text = re.sub(regex, "", text, flags=re.M)
	text = re.sub(opt_out_regex, "", text)
	print(re.findall(regex, text, flags=re.I | re.M))
	return text


def escape_special_characters(text):
	for name in NAME2CODE_POINT:
		char = chr(NAME2CODE_POINT[name])
		text = re.sub(r'\&' + name + r'\;', char, text)
	return text


def print_details_head(text, id):
	regex = re.compile(
		r"(^(((le|sur)\s.*?\n{0,1}.*?(écrit|йcrit):$)|(on\s.*?\n{0,1}.*?wrote:$)|((([0-9]{2}\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))|понедельник|вторник|среда|четверг|пятница|суббота|воскресенье).*?\n{0,1}.*?написал:$)|(El\s.*?\n{0,1}.*?escribió:$)|(201[0-7].*?\n{0,1}.*?(<*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+>*):{0,1}$)))",
		flags=re.M | re.I)
	for head in re.finditer(regex, text):
		if head:
			print(str(id) + '\t' + head.group(0))


def rewrite_details_head(text):
	heads = re.finditer(r'^\?\?\?.*$', text, flags=re.M)
	for head in heads:
		s = int(head.start())
		e = int(head.end())
		new_head = text[s:e]
		new_head = re.sub(r'\sпользователь', '', new_head, flags=re.I)
		new_head = re.sub(r'\:\"', '\"', new_head)
		new_head = re.sub(r'\"$', ''' . . . "''', new_head)
		if re.findall(r'(((\s|,)[^\,\n\r\t]+?)(?=(\s+<*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+>*)))', new_head,
		              flags=re.I):
			new_head = re.sub(r'(\s(<*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+>*))', '', new_head, flags=re.I)
		text = text[:s] + new_head + text[e:]
	return text


def details_head_email_handler(text):
	heads_regex = re.finditer(r'^\?\?\?.*$', text, flags=re.M)
	for head in heads_regex:
		s = int(head.start())
		e = int(head.end())
		new_head = text[s:e]
		email_regex = r"([a-zA-Z0-9_.+-]+\@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,3})"
		for email in re.finditer(email_regex, new_head):
			s = int(email.start())
			e = int(email.end())
			new_email = new_head[s:e]
			try:
				user = User.objects.get(email=new_email)
				print(user.username + '\t')
			except:
				print("Couldn't find user\t")
				continue
