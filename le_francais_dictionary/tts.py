import json
import os
from pathlib import Path

from mutagen.mp3 import EasyMP3
from io import BytesIO

import eyed3
from unidecode import unidecode

from polly.api import PollyAPI
from polly.const import LANGUAGE_CODE_FR as LANGUAGE_FR, \
	LANGUAGE_CODE_RU as LANGUAGE_RU, VOICE_ID_LEA as POLLY_FR_VOICE_FEMALE, \
	VOICE_ID_MATHIEU as POLLY_FR_VOICE_MALE, TEXT_TYPE_SSML, TEXT_TYPE_TEXT, SAMPLE_RATE_22050, OUTPUT_FORMAT_MP3
from pydub import AudioSegment

from polly.models import PollyTask

FTP_FR_WORDS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/FR/'
fr_verbs = FTP_FR_WORDS_PATH + 'verbs/'
fr_verbs_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/verbs/'
FTP_RU_WORDS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/RU/'
FTP_FR_VERBS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/FR/verbs/'
FTP_RU_VERBS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/RU/verbs/'
ru_verbs = FTP_RU_WORDS_PATH + 'verbs/'
ru_verbs_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/verbs/'
GENRE_MASCULINE = 'm'
GENRE_FEMININE = 'f'
GOOGLE_FR_VOICE_MALE = 'Wavenet-D'
GOOGLE_FR_VOICE_FEMALE = 'Wavenet-E'
GOOGLE_FR_VOICE_NEUTRAL = GOOGLE_FR_VOICE_MALE
GOOGLE_RU_VOICE_MALE = 'Wavenet-D'
GOOGLE_RU_VOICE_FEMALE = 'Wavenet-A'
GOOGLE_RU_VOICE_NEUTRAL = GOOGLE_RU_VOICE_MALE

POLLY_FR_VOICE_NEUTRAL = POLLY_FR_VOICE_FEMALE


def get_path(language_code):
	if language_code == LANGUAGE_FR:
		return fr_verbs
	else:
		return ru_verbs

def get_url_path(language_code):
	if language_code == LANGUAGE_FR:
		return fr_verbs_url
	else:
		return ru_verbs_url

def google_cloud_tts(s, filename, language=LANGUAGE_FR, genre=GENRE_FEMININE, file_id=None, file_title=None, ftp_path=None):
	from google.cloud import texttospeech
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=language).voices
	if genre == GENRE_FEMININE:
		voice_name = GOOGLE_FR_VOICE_FEMALE if language == LANGUAGE_FR else GOOGLE_RU_VOICE_FEMALE
	elif genre == GENRE_MASCULINE:
		voice_name = GOOGLE_FR_VOICE_MALE if language == LANGUAGE_FR else GOOGLE_RU_VOICE_MALE
	else:
		voice_name = GOOGLE_FR_VOICE_NEUTRAL if language == LANGUAGE_FR else GOOGLE_RU_VOICE_NEUTRAL
	voice_name = language + '-' + voice_name
	for voice in voices:
		if voice.name == voice_name:
			break
	voice = texttospeech.types.VoiceSelectionParams(
		language_code=language,
		name=voice.name,
	)
	audio_config = texttospeech.types.AudioConfig(
		audio_encoding=texttospeech.enums.AudioEncoding.MP3,
		speaking_rate=0.9,
	)
	synthesis_input = texttospeech.types.SynthesisInput(
		ssml='<speak>{0}</speak>'.format(s)
	)
	response = client.synthesize_speech(synthesis_input, voice, audio_config)
	filename = filename + '.mp3'
	save_audio_stream_to_sftp(response.audio_content, ftp_path or get_path(language), filename, file_id, file_title, voice.name, file_album='Google Cloud')
	return get_url_path(language) + filename


def shtooka_by_title_in_path(title, ftp_path, language_code=LANGUAGE_FR):
	title = unidecode(title).lower().strip()
	path = os.environ.get('SHTOOKA_PATH', None)
	if path is None:
		return None
	map_filename = path.split(r'/')[-1]+'.json'
	map_path = Path(f'le_francais_dictionary/local/mp3_maps/{map_filename}')
	if not map_path.exists():
		titles_map = {}
		d = Path(path)
		for file in d.glob('*.mp3'):
			mp3 = EasyMP3(file)
			if 'title' in mp3.tags:
				t = unidecode(mp3['title'][0]).strip('\r')
			else:
				print(f'{file.name}')
				continue
			titles_map[t] = file.name
		map_file = map_path.open('w', encoding='utf-8')
		json.dump(titles_map, map_file)
	else:
		map_file = map_path.open('r', encoding='utf-8')
		titles_map = json.load(map_file)
	map_file.close()

	if title in titles_map.keys():
		filename = titles_map[title]
		put_to_ftp(filename, f'{path}/{filename}', ftp_path or get_path(language_code))
		# TODO fix different paths to return
		return f'https://files.le-francais.ru/dictionnaires/sound/FR/verbs/{filename}'
	else:
		return None

def amazon_polly_tts(s, filename, language=LANGUAGE_FR, genre=GENRE_FEMININE, file_id=None, file_title=None, return_polly=False, ftp_path=None):
	if genre == GENRE_MASCULINE:
		voice_id = POLLY_FR_VOICE_MALE
	elif genre == GENRE_FEMININE:
		voice_id = POLLY_FR_VOICE_FEMALE
	else:
		voice_id = POLLY_FR_VOICE_NEUTRAL
	polly_task = PollyTask(
		text=s,
		text_type=TEXT_TYPE_TEXT,
		language_code=language,
		sample_rate=SAMPLE_RATE_22050,
		voice_id=voice_id,
		output_format=OUTPUT_FORMAT_MP3,
	)
	stream = polly_task.get_audio_stream()
	save_to_ftp_path = ftp_path or get_path(language)
	filename = filename + '.mp3'
	save_audio_stream_to_sftp(stream.read(), save_to_ftp_path, filename, file_id, file_title, voice_id, file_album='Amazon Polly')
	if return_polly:
		return get_url_path(language) + filename, polly_task
	return get_url_path(language) + filename


def save_audio_stream_to_sftp(audio, path, filename, file_id, file_title,
							  file_author, file_album):
	with BytesIO() as mp3_file:
		mp3_file.write(audio)
		mp3 = EasyMP3(mp3_file)
		mp3.add_tags()
		mp3['tracknumber'] = file_id
		mp3['title'] = file_title
		mp3['artist'] = file_author
		mp3['album'] = file_album
		mp3.save(mp3_file)
		put_to_ftp(filename, mp3_file, path)


def put_to_ftp(filename, mp3_file, path):
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
		if isinstance(mp3_file, str):
			file = open(mp3_file, 'rb')
			srv.putfo(file, filename)
			file.close()
		else:
			file = mp3_file
			file.seek(0)
			srv.putfo(file, filename)
	return True
