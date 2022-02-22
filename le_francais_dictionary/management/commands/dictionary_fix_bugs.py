# -*- coding: utf-8 -*-
import csv
from io import BytesIO
from pathlib import Path

from django.core.management import BaseCommand
from mutagen.mp3 import EasyMP3

from custom_user.models import User
from le_francais_dictionary.consts import GENRE_FEMININE, GENRE_MASCULINE
from le_francais_dictionary.models import Word, UserStandalonePacket
from le_francais_dictionary.tts import put_to_ftp, FTP_FR_WORDS_PATH, FTP_RU_WORDS_PATH, FR_WORDS_URL, RU_WORDS_URL

COL_ID = 'ID'
COL_RU_REWRITE = 'RU REWRITE'
COL_RU_SYNTH_STRING = 'RU SYNTH STRING'
COL_RU_MP3 = 'RU MP3'
COL_FR_REWRITE = 'FR REWRITE'
COL_FR_SYNTH_STRING = 'FR SYNTH STRING'
COL_FR_MP3 = 'FR MP3'
COL_PLACE = 'Место'
COL_DETAILS = 'Детали'
COL_ACTION = 'ACTION'
COL_GENRE = 'GEN'

DETAILS_MASCULINE_TO_FEMININE = 'ж.р. произносится м. голосом'
DETAILS_FEMININE_TO_MASCULINE = 'м.р. произносится ж. голосом'

PLACE_RU = 'рус.'
PLACE_FR = 'фр.'
PLACE_RU_FR = 'фр. & рус.'

ACTION_REWRITE = 'изменить карточку'
ACTION_REVOICE = 'переозвучить'
ACTION_REPLACE_FILE = 'поменять файл озвучки'
ACTION_REWRITE_REVOICE = 'изменить карточку и переозвучить'
ACTION_REWRITE_REPLACE_FILE = 'изменить карточку и поменять файл озвучки'
ACTION_REWRITE_REPLACE_REVOICE = 'изменить карточку, переозвучить и поменять файл озвучки'

def tag_file(path, tag_values):
    new_mp3_file = BytesIO()
    new_mp3_file.write(path.read_bytes())
    mp3_tags = EasyMP3(new_mp3_file)
    if mp3_tags.tags is None:
        mp3_tags.add_tags()
    for tag, value in tag_values:
        mp3_tags.tags[tag] = value
    mp3_tags.save(new_mp3_file)
    return new_mp3_file

class Command(BaseCommand):
    def handle(self, *args, **options):
        table = open(
            'le_francais_dictionary/local/Dictionary updated - BUGS 02.tsv',
            'r',
            encoding='utf-8'
        )
        #
        # table_reader = csv.DictReader(table, dialect=csv.excel_tab)
        #
        # words_ids = [int(r[COL_ID]) for r in table_reader if r[COL_ID]]
        # admins = User.objects.filter(pk__in=[24, 763])
        # for admin in admins:
        #     standalone_packet, created = UserStandalonePacket.objects.get_or_create(user=admin)
        #     standalone_packet.words = words_ids
        #     standalone_packet.filters = None
        #     standalone_packet.save()
        # table.seek(0)
        #
        table_reader = csv.DictReader(table, dialect=csv.excel_tab)
        for row in table_reader:
            cd_id = row[COL_ID]
            word = Word.objects.get(cd_id=cd_id)
            print(word)
            place = row[COL_PLACE]
            details = row[COL_DETAILS]
            action = row[COL_ACTION]
            if details == DETAILS_MASCULINE_TO_FEMININE and word.genre == GENRE_MASCULINE:
                word.genre = GENRE_FEMININE
            elif details == DETAILS_FEMININE_TO_MASCULINE and word.genre == GENRE_FEMININE:
                word.genre = GENRE_MASCULINE
            if row[COL_FR_MP3] or row[COL_FR_REWRITE] or row[COL_FR_SYNTH_STRING] or place in [PLACE_FR, PLACE_RU_FR] or row[COL_GENRE]:
                if row[COL_FR_REWRITE]:
                    word.word = row[COL_FR_REWRITE]
                if row[COL_FR_SYNTH_STRING]:
                    word.word_ssml = f'{row[COL_FR_SYNTH_STRING]}'
                    word.local_voice()
                if row[COL_FR_MP3]:
                    path = Path(f'D:/Sound/SoundF3/{row[COL_FR_MP3]}')
                    if path.exists():
                        new_file = tag_file(path, [
                            ('title', word.word),
                            ('tracknumber', str(word.cd_id)),
                            ('copyright', 'www.le-francais.ru'),
                            ('composer', 'ILYA DUMOV')
                        ])
                        put_to_ftp(row[COL_FR_MP3], new_file, FTP_FR_WORDS_PATH)
                        new_file.close()
                    url = FR_WORDS_URL + row[COL_FR_MP3]
                    word._polly_url = url
                if row[COL_GENRE]:
                    word.genre = row[COL_GENRE]
                word.save()

            if row[COL_RU_REWRITE] or row[COL_RU_SYNTH_STRING] or row[COL_RU_MP3] or place in [PLACE_RU, PLACE_RU_FR]:
                translation = word.first_translation
                if row[COL_RU_REWRITE]:
                    translation.translation = row[COL_RU_REWRITE]
                if row[COL_RU_SYNTH_STRING]:
                    translation.translations_ssml = f'{row[COL_RU_SYNTH_STRING]}'
                    translation.local_voice()
                if row[COL_RU_MP3]:
                    path = Path(f'D:/Sound/RussianBX3/{row[COL_RU_MP3]}')
                    if path.exists():
                        new_file = tag_file(path, [
                            ('title', translation.translation),
                            ('tracknumber', str(word.cd_id)),
                            ('copyright', 'www.le-francais.ru'),
                            ('composer', 'ILYA DUMOV')
                        ])
                        put_to_ftp(row[COL_RU_MP3], new_file, FTP_RU_WORDS_PATH)
                        new_file.close()
                    url = RU_WORDS_URL + row[COL_RU_MP3]
                    translation._polly_url = url
                translation.save()
