import csv
import sys
from typing import List, Tuple
from urllib import request

import requests
from bulk_update.helper import bulk_update
from django.core.management import BaseCommand, CommandParser
from django.db import transaction

from custom_user.models import User
from home.models import LessonPage
from le_francais_dictionary.consts import GENRE_FEMININE
from le_francais_dictionary.models import Word, WordTranslation, \
    WordGroup, UnifiedWord, Packet, UserPacket, UserStandalonePacket


def parse_tables(words_table_path, groups_table_path):
    words_table = []
    with open(words_table_path, 'r', encoding='utf-8') as f:
        words_csv_reader = csv.DictReader(f)
        for row in words_csv_reader:
            words_table.append(row)
    groups_table = []
    with open(groups_table_path, 'r', encoding='utf-8') as f:
        groups_csv_reader = csv.DictReader(f)
        for row in groups_csv_reader:
            groups_table.append(row)
    return words_table, groups_table


def str2ssml(str):
    if not '<speak>' in str:
        ssml = f'<speak>{str.strip()}</speak>'
    else:
        ssml = str
    return ssml


def create_words_translations(words_table):
    # IDX
    # NO
    # NEW_WORD
    # TRANSLATION
    # GOOGLE_TRANSLATE
    # PRONONSATION R
    # PRONONSATION F
    # POS
    # GEN
    existing_translations = {t.word_id:(t, False) for t in WordTranslation.objects.all()}
    existing_words = {w.pk:(w, False) for w in Word.objects.all()}
    new_words = []
    new_translations = []
    for row in words_table:
        if '' in (row['IDX'], row['NEW_WORD']):
            continue
        word_cd_id = int(row['IDX'])
        if not word_cd_id in existing_words.keys():
            word = Word(
                cd_id=word_cd_id,
                word=row['NEW_WORD'],
                word_ssml=str2ssml(row['PRONONSATION F']),
                genre=row['GEN'],
                part_of_speech=row['POS']
            )
            existing_words[word.pk] = (word, True)
        else:
            word, created_word = existing_words[word_cd_id]
            word.word = row['NEW_WORD']
            word.word_ssml = str2ssml(row['PRONONSATION F'])
            word.genre = row['GEN']
            word.part_of_speech = row['POS']
        if not word_cd_id in existing_translations.keys():
            translation = WordTranslation(
                word_id=word_cd_id,
                translation=row['TRANSLATION'],
                translations_ssml=str2ssml(row['PRONONSATION R'])
            )
            existing_translations[translation.word_id] = (translation, True)
        else:
            translation, created_translation = existing_translations[word_cd_id]
            translation.translation = row['TRANSLATION']
            translation.translation_ssml = row['PRONONSATION R']
    return list(existing_words.values()), list(existing_translations.values())


def create_groups(groups_table, words:List[Tuple]):
    # RAFINÉ
    # NOL
    # IDX
    # NO
    # PACK
    # WORD_UNIFIED
    # WORD_ORIG
    # GROUP
    # GROUP_ID
    # TRANSLATION_UNIFIED
    # TRANSLATION_ORIG
    existing_words = {w.cd_id:(w, w_created) for w, w_created in words}
    existing_groups = {wg.pk:(wg, False) for wg in WordGroup.objects.all()}
    existing_unified_words = {(uw.group_id, uw.definition_num):(uw, False) for uw in UnifiedWord.objects.all()}

    for row in groups_table:
        word_id = int(row['IDX'])
        word_u, translation_u = row['WORD_UNIFIED'], row['TRANSLATION_UNIFIED']
        word, translation = row['WORD_ORIG'], row['TRANSLATION_ORIG']
        group_id, definition_num = int(row['GROUP_ID']), int(row['GROUP'])
        if group_id == '':
            continue
        if word_u == '1':
            word_u = word
        if translation_u == '1':
            translation_u = translation

        unified_word, unified_word_created = existing_unified_words.get((group_id, definition_num), (None, None))
        group, group_created = existing_groups.get(group_id, (None, None))

        if group is None:
            group = WordGroup(pk=group_id)
            existing_groups[group_id] = (group, True)

        if unified_word is None:
            unified_word = UnifiedWord(
                group_id=group.pk,
                word=word_u,
                translation=row['TRANSLATION_UNIFIED'],
                definition_num=definition_num
            )
            existing_unified_words[(group_id, definition_num)] = (unified_word, True)
        else:
            if word_u != '':
                unified_word.word = word_u
            if translation_u != '':
                unified_word.translation = translation_u

        w, w_created = existing_words.get(word_id, (None, None))
        w:Word
        if w is not None:
            w.group_id = group_id
            w.definition_num = definition_num
        else:
            raise SystemExit(f'Can not find word with id [{word_id}]')

    return list(existing_groups.values()), list(existing_unified_words.values()), list(existing_words.values())


def save_words(words:List[Tuple], translations:List[Tuple]):
    with transaction.atomic():
        bulk_create_or_update(Word, words)
        bulk_create_or_update(WordTranslation, translations)


def save_groups(groups:List[Tuple], unified_words:List[Tuple], words:List[Tuple], translations:List[Tuple]):
    for unified_word, unified_word_created in unified_words:
        word, word_created = next(((w, created) for w, created in words if w.group_id == unified_word.group_id),None)
        if word is None:
            raise SystemExit(f'Can not find word with group_id: [{unified_word.group_id}]')
        if unified_word.word == '':
            unified_word.word = word.word
        if unified_word.translation == '':
            translation, translation_created = next(((t, created) for t, created in translations if t.word_id == word.pk), None)
            if translation is None:
                raise SystemExit(f'Can not find translation with word_id: [{word.pk}]')
            unified_word.translation = translation.translation
    with transaction.atomic():
        bulk_create_or_update(WordGroup, groups, update=False)
        bulk_create_or_update(UnifiedWord, unified_words)


def bulk_create_or_update(model, objects_list:List[Tuple], update=True):
    model.objects.bulk_create(
        [o for o, created in objects_list if created])
    if update:
        bulk_update([o for o, created in objects_list if not created])


def voice_words(words, translations, groups, unified_words):
    to_save_words = []
    to_save_translations = []
    # voice_objects(to_save_words, words, 'word')
    voice_objects(to_save_translations, translations, 'translation')


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def  voice_objects(to_save, objects, s_field):
    try:
        for object, created in objects:
            if created or not object.polly_url or (object.genre == GENRE_FEMININE and not 'fem' in object.polly_url.split('/')[-1] and not 'SYNTH' in object.polly_url.upper().split('/')[-1]) or (
               not url_ok(object.polly_url)
            ):
                print(f'Word: {getattr(object, s_field)}')
                print(f'Word: {object.get_ssml()}')
                object.voice(save=False)
                print(object.polly_url)
                to_save.append(object)
    except:
        bulk_update(to_save, update_fields=['_polly_url'])
        e, traceback = sys.exc_info()[1:]
        print(e)
        raise SystemExit('Error while voicing')
    bulk_update(to_save, update_fields=['_polly_url'])


def add_words_to_packets(words_table):
    # IDX
    # NO
    # NEW_WORD
    # TRANSLATION
    # GOOGLE_TRANSLATE
    # PRONONSATION R
    # PRONONSATION F
    # POS
    # GEN
    empty_packets = Packet.objects.filter(word=None)
    empty_packets.delete()
    words = {w.cd_id:w for w in Word.objects.all()}
    lessons = {l.lesson_number:l for l in LessonPage.objects.all()}
    packets = {p.name:p for p in Packet.objects.all()}
    for row in words_table:
        if not row['IDX']:
            continue
        cd_id = int(row['IDX'])
        n = int(row['NO'])
        packet_name = f'урок {n}'
        print(packet_name)
        if not packet_name in packets.keys():
            packet = Packet.objects.create(
                name=packet_name,
                demo=False,
                lesson=lessons[n]
            )
            packets[packet_name] = packet
        else:
            packet = packets[packet_name]

        word = words[cd_id]
        word.packet = packet
    bulk_update(list(words.values()), update_fields=['packet'])


def admin_packet(words_table):
    user = User.objects.get(username='ILYA DUMOV')
    packet = UserStandalonePacket.objects.get(user=user)
    packet.words = [w.cd_id for w, created in words if created]
    packet.save()


class Command(BaseCommand):
    def add_arguments(self, parser:CommandParser):
        parser.add_argument('--words_table', dest='words_table')
        parser.add_argument('--groups_table', dest='groups_table')

    def handle(self, *args, **options):
        words_table, groups_table = parse_tables(options['words_table'], options['groups_table'])
        words, translations = create_words_translations(words_table)
        groups, unified_words, words_to_update = create_groups(groups_table, words)
        # save_groups(groups, unified_words, words, translations)
        # save_words(words, translations)
        voice_words(words, translations, groups, unified_words)
        # add_words_to_packets(words_table)
        # admin_packet(words_table)
