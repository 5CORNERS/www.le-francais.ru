# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re
import difflib

# Regex patterns for HTML tag protection
TAG_RE = re.compile(r'(<[^>]+>)')


def _protect_html_tags(text):
    """
    Splits text into chunks of (is_tag, chunk).
    Ensures that text manipulation only touches text content, NOT HTML tag names or attributes.
    """
    parts = []
    last_end = 0
    for m in TAG_RE.finditer(text):
        if m.start() > last_end:
            parts.append((False, text[last_end:m.start()]))
        parts.append((True, m.group(0)))
        last_end = m.end()
    if last_end < len(text):
        parts.append((False, text[last_end:]))
    return parts


def fix_typography(text):
    """
    Applies typography rules:
    - Straight quotes "..." to Russian guillemets «...»
    - Space-padded hyphens ' - ' to em-dash ' — '
    """
    reasons = []

    # 0. Suffixes/prefixes with accidental space after hyphen: 'на - ayer' -> 'на -ayer', ', - ondre' -> ', -ondre'
    if re.search(r'(\b(?:на|оканчивающихся\s+на|заканчивающихся\s+на|заканчивается\s+на|суффикс)\s+)-\s+([a-zа-яё]+)\b', text, re.IGNORECASE):
        text = re.sub(r'(\b(?:на|оканчивающихся\s+на|заканчивающихся\s+на|заканчивается\s+на|суффикс)\s+)-\s+([a-zа-яё]+)\b', r'\1-\2', text, flags=re.IGNORECASE)
    if re.search(r'([,\(\[\{]\s*)-\s+([a-zа-яё]+)\b', text, re.IGNORECASE):
        text = re.sub(r'([,\(\[\{]\s*)-\s+([a-zа-яё]+)\b', r'\1-\2', text, flags=re.IGNORECASE)

    # 1. Hyphens to Em-Dashes (space-padded only, avoiding intra-word hyphens like 'quelque-chose')
    if re.search(r'(?<=\S)\s+-\s+(?=\S)', text):
        text = re.sub(r'(?<=\S)\s+-\s+(?=\S)', ' — ', text)
        reasons.append(('тире', 'Замена дефиса с пробелами на длинное тире (« — »)'))

    # 2. Quotation marks: straight quotes to Russian guillemets «...»
    # Skip if quote is inside an HTML attribute (which is protected by chunking)
    if '"' in text:
        # Regex to pair quotes around words
        new_text = re.sub(r'"([^"\n\r]+)"', r'«\1»', text)
        # Handle french spacing if french quotes: « mot »
        if new_text != text:
            text = new_text
            reasons.append(('кавычки', 'Замена прямых кавычек на кавычки-ёлочки («...»)'))

    return text, reasons


def fix_abbreviations_and_spacing(text):
    """
    Fixes abbreviations, missing spaces, and informal abbreviations:
    - 'т.е.' -> 'т. е.'
    - 'т.д.' -> 'т. д.'
    - 'т.п.' -> 'т. п.'
    - 'и т.д.' -> 'и т. д.'
    - 'и т.п.' -> 'и т. п.'
    - 'женск.' / 'жен.' -> 'женского рода' / 'женский род'
    - 'муж.' / 'мужск.' -> 'мужского рода' / 'мужской род'
    - 'франц.' -> 'французском' / 'французский'
    - 'англ.' -> 'английском' / 'английский'
    """
    reasons = []

    # Spaces in abbreviations
    if re.search(r'\bт\.е\.', text):
        text = re.sub(r'\bт\.е\.', 'т. е.', text)
        reasons.append(('т. е.', 'Добавлен пробел в сокращении «т. е.»'))

    if re.search(r'\bт\.д\.', text):
        text = re.sub(r'\bт\.д\.', 'т. д.', text)
        reasons.append(('т. д.', 'Добавлен пробел в сокращении «т. д.»'))

    if re.search(r'\bт\.п\.', text):
        text = re.sub(r'\bт\.п\.', 'т. п.', text)
        reasons.append(('т. п.', 'Добавлен пробел в сокращении «т. п.»'))

    if re.search(r'\bт\.к\.', text):
        text = re.sub(r'\bт\.к\.', 'т. к.', text)
        reasons.append(('т. к.', 'Добавлен пробел в сокращении «т. к.»'))

    # Abbreviations expansion
    # 'в женск. роде' -> 'в женском роде', 'женск. род' -> 'женский род', '(женск.)' -> '(женский род)'
    if re.search(r'\bженск\.\s*роде\b', text, re.IGNORECASE):
        text = re.sub(r'\bженск\.\s*роде\b', 'женском роде', text, flags=re.IGNORECASE)
        reasons.append(('женск.', 'Раскрыто сокращение «женск. роде» -> «женском роде»'))
    if re.search(r'\bженск\.\s*рода\b', text, re.IGNORECASE):
        text = re.sub(r'\bженск\.\s*рода\b', 'женского рода', text, flags=re.IGNORECASE)
        reasons.append(('женск.', 'Раскрыто сокращение «женск. рода» -> «женского рода»'))
    if re.search(r'\bженск\.\s*род\b', text, re.IGNORECASE):
        text = re.sub(r'\bженск\.\s*род\b', 'женский род', text, flags=re.IGNORECASE)
        reasons.append(('женск.', 'Раскрыто сокращение «женск. род» -> «женский род»'))
    if re.search(r'\bженск\.\b', text, re.IGNORECASE):
        text = re.sub(r'\bженск\.\b', 'женского рода', text, flags=re.IGNORECASE)
        reasons.append(('женск.', 'Раскрыто сокращение «женск.» -> «женского рода»'))

    if re.search(r'\bмуж\.\s*роде\b', text, re.IGNORECASE):
        text = re.sub(r'\bмуж\.\s*роде\b', 'мужском роде', text, flags=re.IGNORECASE)
        reasons.append(('муж.', 'Раскрыто сокращение «муж. роде» -> «мужском роде»'))
    if re.search(r'\bмуж\.\s*рода\b', text, re.IGNORECASE):
        text = re.sub(r'\bмуж\.\s*рода\b', 'мужского рода', text, flags=re.IGNORECASE)
        reasons.append(('муж.', 'Раскрыто сокращение «муж. рода» -> «мужского рода»'))
    if re.search(r'\bмуж\.\s*род\b', text, re.IGNORECASE):
        text = re.sub(r'\bмуж\.\s*род\b', 'мужской род', text, flags=re.IGNORECASE)
        reasons.append(('муж.', 'Раскрыто сокращение «муж. род» -> «мужской род»'))

    # 'франц. языке' -> 'французском языке', 'франц. язык' -> 'французский язык'
    if re.search(r'\bфранц\.\s*языке\b', text, re.IGNORECASE):
        text = re.sub(r'\bфранц\.\s*языке\b', 'французском языке', text, flags=re.IGNORECASE)
        reasons.append(('франц.', 'Раскрыто сокращение «франц. языке» -> «французском языке»'))
    if re.search(r'\bфранц\.\s*язык\b', text, re.IGNORECASE):
        text = re.sub(r'\bфранц\.\s*язык\b', 'французский язык', text, flags=re.IGNORECASE)
        reasons.append(('франц.', 'Раскрыто сокращение «франц. язык» -> «французский язык»'))

    # 'англ. языке' -> 'английском языке', 'англ. язык' -> 'английский язык'
    if re.search(r'\bангл\.\s*языке\b', text, re.IGNORECASE):
        text = re.sub(r'\bангл\.\s*языке\b', 'английском языке', text, flags=re.IGNORECASE)
        reasons.append(('англ.', 'Раскрыто сокращение «англ. языке» -> «английском языке»'))
    if re.search(r'\bангл\.\s*язык\b', text, re.IGNORECASE):
        text = re.sub(r'\bангл\.\s*язык\b', 'английский язык', text, flags=re.IGNORECASE)
        reasons.append(('англ.', 'Раскрыто сокращение «англ. язык» -> «английский язык»'))

    return text, reasons


def fix_grammar_and_punctuation(text):
    """
    Fixes grammar, punctuation, and common typos:
    - 'также как' / 'так же как' -> 'так же, как'
    - Missing comma before 'как в примере' (ONLY if not preceded by dash, comma, colon, dot, etc.)
    - Incorrect numeral affixes (e.g. '1-ый' -> '1-й', '2-ой' -> '2-й')
    - 'в течении' (времени) -> 'в течение'
    - 'сответствие' -> 'соответствие'
    """
    reasons = []

    # 1. 'также' vs 'так же' before 'как':
    # 'также, как' -> 'так же, как'
    if re.search(r'\bтакже,\s*как\b', text, re.IGNORECASE):
        text = re.sub(r'\bтакже,\s*как\b', 'так же, как', text, flags=re.IGNORECASE)
        reasons.append(('так же', 'Замена слитного «также» на раздельное «так же» перед «как»'))
    # 'также как' -> 'так же, как'
    elif re.search(r'\bтакже\s+как\b', text, re.IGNORECASE):
        text = re.sub(r'\bтакже\s+как\b', 'так же, как', text, flags=re.IGNORECASE)
        reasons.append(('так же, как', 'Замена «также как» на «так же, как» с запятой'))
    # 'так же как' -> 'так же, как' (missing comma between 'так же' and 'как')
    elif re.search(r'\bтак\s+же\s+как\b', text, re.IGNORECASE):
        text = re.sub(r'\bтак\s+же\s+как\b', 'так же, как', text, flags=re.IGNORECASE)
        reasons.append(('запятая', 'Добавлена запятая между «так же» и «как»'))

    # 2. Comma before 'как в примере':
    # ONLY add comma if preceded by a letter, digit, closing quote, etc.
    # NEVER add comma if already preceded by dash (—, –, -, ―, ‒, −), comma (,), colon (:),
    # semicolon (;), period (.), exclamation (!), question (?), opening brackets/quotes, or ellipsis (…).
    if re.search(r'([^\s,;:\.!?…—–\-\―\‒\−\(\[«"])\s+как\s+в\s+примере\b', text, re.IGNORECASE):
        text = re.sub(r'([^\s,;:\.!?…—–\-\―\‒\−\(\[«"])\s+как\s+в\s+примере\b', r'\1, как в примере', text, flags=re.IGNORECASE)
        reasons.append(('запятая', 'Добавлена запятая перед оборотом «как в примере»'))

    # 3. Comma before 'так же, как в примере' if missed before 'так же':
    if re.search(r'([^\s,;:\.!?…—–\-\―\‒\−\(\[«"])\s+так\s+же,\s*как\s+в\s+примере\b', text, re.IGNORECASE):
        text = re.sub(r'([^\s,;:\.!?…—–\-\―\‒\−\(\[«"])\s+так\s+же,\s*как\s+в\s+примере\b', r'\1, так же, как в примере', text, flags=re.IGNORECASE)
        reasons.append(('запятая', 'Добавлена запятая перед оборотом «так же, как в примере»'))

    # 4. Numeral affixes standard Russian rules:
    # 1-ый -> 1-й, 2-ой -> 2-й, 3-ий -> 3-й, 5-ти -> 5-ти/5-го
    # Common mistakes in Russian: 1-ый, 2-ой, 3-ий, 4-ый, 5-ый, 6-ой, 7-ой, 8-ой
    text_sub = re.sub(r'\b(\d+)-(?:ый|ой|ий)\b', r'\1-й', text)
    if text_sub != text:
        text = text_sub
        reasons.append(('наращение', 'Исправлено наращение числительного (например, «1-й» вместо «1-ый»)'))

    text_sub = re.sub(r'\b(\d+)-(?:ая|яя)\b', r'\1-я', text)
    if text_sub != text:
        text = text_sub
        reasons.append(('наращение', 'Исправлено наращение числительного (например, «1-я» вместо «1-ая»)'))

    text_sub = re.sub(r'\b(\d+)-(?:ое|ее)\b', r'\1-е', text)
    if text_sub != text:
        text = text_sub
        reasons.append(('наращение', 'Исправлено наращение числительного (например, «1-е» вместо «1-ое»)'))

    text_sub = re.sub(r'\b(\d+)-(?:ые|ие)\b', r'\1-е', text)
    if text_sub != text:
        text = text_sub
        reasons.append(('наращение', 'Исправлено наращение числительного (например, «2-е» вместо «2-ые»)'))

    # 5. Common spelling errors
    if re.search(r'\bв течении\b(?=\s+(?:дня|недели|месяца|года|урока|времени|минуты|часа|двух|трех|нескольких))', text, re.IGNORECASE):
        text = re.sub(r'\bв течении\b(?=\s+(?:дня|недели|месяца|года|урока|времени|минуты|часа|двух|трех|нескольких))', 'в течение', text, flags=re.IGNORECASE)
        reasons.append(('в течение', 'Исправлено «в течении» -> «в течение» (временной предлог)'))

    if re.search(r'\bсответстви[еяю]\b', text, re.IGNORECASE):
        text = re.sub(r'\bсответстви', 'соответстви', text, flags=re.IGNORECASE)
        reasons.append(('опечатка', 'Исправлена опечатка «сответствие» -> «соответствие»'))

    return text, reasons


def proofread_text(original_text):
    """
    Main entrypoint to proofread an exercise text field.
    Protects HTML tags and processes only human-readable text parts.
    Returns: (suggested_text, list_of_reasons)
    """
    if not original_text or not original_text.strip():
        return original_text, []

    # Replace HTML tags with private Unicode placeholders
    tag_map = {}
    def _save_tag(m):
        idx = len(tag_map)
        token = '\ue000TAG_%d\ue001' % idx
        tag_map[token] = m.group(0)
        return token

    masked_text = TAG_RE.sub(_save_tag, original_text)

    all_reasons = []

    # 1. Typography
    t1, r1 = fix_typography(masked_text)
    # 2. Abbreviations & spacing
    t2, r2 = fix_abbreviations_and_spacing(t1)
    # 3. Grammar & punctuation
    t3, r3 = fix_grammar_and_punctuation(t2)

    all_reasons = r1 + r2 + r3

    # Restore HTML tags
    suggested = t3
    for token, orig_tag in tag_map.items():
        suggested = suggested.replace(token, orig_tag)

    # De-duplicate reasons by tag
    seen_tags = set()
    deduped_reasons = []
    for tag, desc in all_reasons:
        if tag not in seen_tags:
            seen_tags.add(tag)
            deduped_reasons.append({'tag': tag, 'description': desc})

    return suggested, deduped_reasons


def build_inline_diff_html(orig_text, sugg_text):
    """
    Constructs a visual HTML diff string with <del> and <ins> highlighting words.
    """
    orig_words = re.findall(r'\S+|\s+', orig_text)
    sugg_words = re.findall(r'\S+|\s+', sugg_text)

    matcher = difflib.SequenceMatcher(None, orig_words, sugg_words)
    diff_html = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            diff_html.append("".join(orig_words[i1:i2]))
        elif tag == 'delete':
            deleted = "".join(orig_words[i1:i2])
            diff_html.append('<del class="diff-del">%s</del>' % _escape_html(deleted))
        elif tag == 'insert':
            inserted = "".join(sugg_words[j1:j2])
            diff_html.append('<ins class="diff-ins">%s</ins>' % _escape_html(inserted))
        elif tag == 'replace':
            deleted = "".join(orig_words[i1:i2])
            inserted = "".join(sugg_words[j1:j2])
            diff_html.append('<del class="diff-del">%s</del><ins class="diff-ins">%s</ins>' % (_escape_html(deleted), _escape_html(inserted)))

    return "".join(diff_html)


def _escape_html(s):
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;')
             .replace("'", '&#039;'))
