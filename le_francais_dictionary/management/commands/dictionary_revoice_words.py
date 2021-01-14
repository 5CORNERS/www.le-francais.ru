import json
import os
from pathlib import Path

from django.core.management import BaseCommand
from mutagen.mp3 import EasyMP3

from le_francais_dictionary.consts import GENRE_MASCULINE
from le_francais_dictionary.models import Word
from le_francais_dictionary.tts import FTP_FR_WORDS_PATH, \
    FTP_RU_WORDS_PATH, PYTTX_FR_M_VOICE, delete_ftp_file, pytts_voice_string
from le_francais_dictionary.utils import remove_parenthesis, \
    clean_filename


def build_file_map(path):
    map_path = Path(
        f'le_francais_dictionary/local/ftp_maps/{"_".join(path.split("/")[-3:])}.json')
    if not map_path.exists():
        file_map = []
        import pysftp
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        srv = pysftp.Connection(
            host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
            username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
            password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
            cnopts=cnopts
        )
        with srv.cd(path):
            files = srv.listdir()
            for n, filename in enumerate(files):
                print(f'{n}/{len(files)}')
                if not '.mp3' in filename:
                    continue
                f = srv.open(filename, 'r', bufsize=300)
                mp3 = EasyMP3(f)
                file_tags = dict(mp3.tags)
                file_tags['filename'] = filename
                file_map.append(file_tags)
                f.close()
        map_file = map_path.open('w', encoding='utf-8')
        json.dump(file_map, map_file)
    else:
        map_file = map_path.open('r', encoding='utf-8')
        file_map = json.load(map_file)
    map_file.close()
    return file_map


def save_map_to_json(files_map, path):
    map_path = Path(
        f'le_francais_dictionary/local/ftp_maps/{"_".join(path.split("/")[-3:])}.json')
    map_file = map_path.open('w', encoding='utf-8')
    json.dump(files_map, map_file)

class Command(BaseCommand):
    def handle(self, *args, **options):
        path = FTP_FR_WORDS_PATH
        existing_files_map = build_file_map(path)
        words = {w.cd_id:w for w in Word.objects.all()}
        for i, mp3_tags in reversed(list(enumerate(existing_files_map))):
            if 'tracknumber' in mp3_tags.keys() and 'artist' in mp3_tags.keys() and 'album' in mp3_tags.keys():
                cd_id_str = mp3_tags['tracknumber'][0]
                artist_str = mp3_tags['artist'][0]
                album_str = mp3_tags['album'][0]
                if cd_id_str and cd_id_str != 'N/A':
                    cd_id = int(cd_id_str)
                else:
                    continue
                if not cd_id in words.keys():
                    continue
                else:
                    word = words[cd_id]
                if word.genre == GENRE_MASCULINE and 'Google Cloud' in album_str:
                    print(word, end='')
                    delete_ftp_file(mp3_tags['filename'], path)
                    existing_files_map.pop(i)
                    s = word.get_ssml()
                    additional_words = [w for w in words.values() if w._polly_url == word._polly_url and w.cd_id != word.cd_id]
                    filename = remove_parenthesis(clean_filename(word.word))
                    url = pytts_voice_string(s, ssml=True,
                                       filename=filename+'_synth_hom',
                                       tag_id=word.pk,
                                       tag_title=word.word,
                                       genre=GENRE_MASCULINE)
                    word._polly_url = url
                    word.save()
                    for w in additional_words:
                        w._polly_url = url
                        w.save()
                    print('\tDone!')
                    existing_files_map.append({
                        'filename': filename+'.mp3',
                        'tracknumber':[word.cd_id],
                        'artist': [PYTTX_FR_M_VOICE],
                        'album':['pyttsx3']
                    })
