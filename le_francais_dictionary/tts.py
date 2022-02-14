import json
import os
from pathlib import Path
from typing import List, Tuple

import requests
from mutagen.mp3 import EasyMP3, HeaderNotFoundError
from io import BytesIO

from unidecode import unidecode

from le_francais_dictionary.consts import GENRE_MASCULINE, \
	GENRE_FEMININE
from le_francais_dictionary.utils import escape_non_url_characters, \
	remove_parenthesis, clean_filename, copy_file

from polly.const import LANGUAGE_CODE_FR as LANGUAGE_FR, \
	LANGUAGE_CODE_RU as LANGUAGE_RU, \
	VOICE_ID_LEA as POLLY_FR_VOICE_FEMALE, \
	VOICE_ID_MATHIEU as POLLY_FR_VOICE_MALE, TEXT_TYPE_SSML, \
	TEXT_TYPE_TEXT, SAMPLE_RATE_22050, OUTPUT_FORMAT_MP3

from polly.models import PollyTask

FTP_FR_WORDS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/FR/'
FR_VERBS_URL = 'https://files.le-francais.ru/dictionnaires/sound/FR/verbs/'
FR_WORDS_URL = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
FTP_RU_WORDS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/RU/'
FTP_FR_VERBS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/FR/verbs/'
FTP_RU_VERBS_PATH = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/RU/verbs/'
RU_VERBS_URL = 'https://files.le-francais.ru/dictionnaires/sound/RU/verbs/'
RU_WORDS_URL = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
GOOGLE_FR_VOICE_MALE = 'Wavenet-D'
GOOGLE_FR_VOICE_FEMALE = 'Wavenet-E'
GOOGLE_FR_VOICE_NEUTRAL = GOOGLE_FR_VOICE_MALE
GOOGLE_RU_VOICE_MALE = 'Wavenet-D'
GOOGLE_RU_VOICE_FEMALE = 'Wavenet-A'
GOOGLE_RU_VOICE_NEUTRAL = GOOGLE_RU_VOICE_MALE

POLLY_FR_VOICE_NEUTRAL = POLLY_FR_VOICE_FEMALE

FTP_PATHS = {
	'words': {
		LANGUAGE_FR: FTP_FR_WORDS_PATH,
		LANGUAGE_RU: FTP_RU_WORDS_PATH
	},
	'verbs': {
		LANGUAGE_FR: FTP_FR_VERBS_PATH,
		LANGUAGE_RU: FTP_RU_VERBS_PATH
	}
}
URL_PATHS = {
	'words': {
		LANGUAGE_FR: FR_WORDS_URL,
		LANGUAGE_RU: RU_WORDS_URL
	},
	'verbs': {
		LANGUAGE_FR: FR_VERBS_URL,
		LANGUAGE_RU: RU_VERBS_URL
	}
}


def get_path(language_code, verbs=False):
	return FTP_PATHS['verbs' if verbs else 'words'][language_code]

def get_url_path(language_code, verbs=False):
	return URL_PATHS['verbs' if verbs else 'words'][language_code]

def google_cloud_tts(s, filename, language=LANGUAGE_FR, genre=GENRE_FEMININE, file_id=None, file_title=None, ftp_path=None, speaking_rate=None, ssml=False, verbs=False):
	if check_if_file_exists(filename+'.mp3', ftp_path or get_path(language)):
		return get_url_path(language, verbs=verbs) + filename + '.mp3'
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
	voice = texttospeech.VoiceSelectionParams(
		language_code=language,
		name=voice.name,
	)
	audio_config = texttospeech.AudioConfig(
		audio_encoding=texttospeech.AudioEncoding.MP3,
		speaking_rate=speaking_rate or 0.9,
	)
	if ssml:
		synthesis_input = texttospeech.SynthesisInput(
			ssml=s
		)
	else:
		synthesis_input = texttospeech.SynthesisInput(
			ssml='<speak>{0}</speak>'.format(s)
		)
	response = client.synthesize_speech(input=synthesis_input,voice=voice,audio_config=audio_config)
	filename = filename + '.mp3'
	try:
		save_audio_stream_to_sftp(response.audio_content, ftp_path or get_path(language), filename, file_id, file_title, voice.name, file_album='Google Cloud')
	except HeaderNotFoundError:
		print(f'ERROR!! Can\'t voice: "{s}"' )
		return None
	return get_url_path(language, verbs=verbs) + filename


def shtooka_by_title_in_path(title, ftp_path, filename=None, language_code=LANGUAGE_FR, genre=GENRE_FEMININE, verbs=False):
	title = title.lower().strip()
	path = os.environ.get('SHTOOKA_PATH', None)
	second_path = os.environ.get('SHTOOKA_PATH_SECOND', None)
	if path is None:
		return None
	if ftp_path is None:
		ftp_path = get_path(language_code, verbs)
	titles_map = get_titles_map(path)
	titles_map_second = get_titles_map(second_path)

	if title in titles_map.keys():
		mp3_filename = titles_map[title]
		if not filename:
			filename = mp3_filename
		else:
			filename = filename+f'.{mp3_filename.split(".")[-1]}'
		if genre == GENRE_FEMININE and not 'fem' in mp3_filename:
			if check_if_file_exists(filename, ftp_path or get_path(language_code=language_code, verbs=verbs)):
				delete_ftp_file(filename, ftp_path or get_path(language_code=language_code, verbs=verbs))
			return None

		put_to_ftp(filename,
				   f'{path}/{mp3_filename}',
				   ftp_path or get_path(language_code))
		# TODO fix different paths to return
		return f'{get_url_path(language_code, verbs=verbs)}{filename}'
	elif title in titles_map_second.keys():
		mp3_filename = titles_map_second[title]
		if not filename:
			filename = mp3_filename
		else:
			filename = filename+f'.{mp3_filename.split(".")[-1]}'
		if genre == GENRE_FEMININE and not 'fem' in mp3_filename:
			if check_if_file_exists(filename, ftp_path or get_path(language_code=language_code, verbs=verbs)):
				delete_ftp_file(filename, ftp_path or get_path(language_code=language_code, verbs=verbs))
			return None

		put_to_ftp(filename, f'{second_path}/{mp3_filename}',
				   ftp_path or get_path(language_code))
		# TODO fix different paths to return
		return f'{get_url_path(language_code, verbs=verbs)}{filename}'
	else:
		return None


def get_titles_map(path):
	map_filename = path.split(r'/')[-1] + '.json'
	map_path = Path(
		f'le_francais_dictionary/local/mp3_maps/{map_filename}')
	if not map_path.exists():
		titles_map = {}
		d = Path(path)
		for file in d.glob('*.mp3'):
			mp3 = EasyMP3(file)
			if 'title' in mp3.tags:
				t = mp3['title'][0].lower().strip('\r')
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
	return titles_map


def amazon_polly_tts(s, filename, language=LANGUAGE_FR,
                     genre=GENRE_FEMININE, file_id=None,
                     file_title=None, return_polly=False,
                     ftp_path=None, verbs=False):
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
	save_to_ftp_path = ftp_path or get_path(language, verbs)
	filename = filename + '.mp3'
	save_audio_stream_to_sftp(stream.read(), save_to_ftp_path, filename, file_id, file_title, voice_id, file_album='Amazon Polly')
	if return_polly:
		return get_url_path(language, verbs) + filename, polly_task
	return get_url_path(language, verbs) + filename


def save_audio_stream_to_sftp(audio, path, filename, file_id, file_title,
							  file_author, file_album):
	with BytesIO() as mp3_file:
		mp3_file.write(audio)
		mp3 = EasyMP3(mp3_file)
		mp3.add_tags()
		mp3['tracknumber'] = str(file_id)
		mp3['title'] = file_title
		mp3['artist'] = file_author
		mp3['album'] = file_album
		mp3.save(mp3_file)
		put_to_ftp(filename, mp3_file, path)


def delete_ftp_file(filename, path):
	srv = get_sftp_srv()
	with srv.cd(path):
		if srv.exists(filename):
			srv.remove(filename)
			return 1
		else:
			return 0


def check_if_file_exists(filename, path):
	srv = get_sftp_srv()
	with srv.cd(path):
		if srv.exists(filename):
			return True
		else:
			return False


def get_sftp_srv():
	import pysftp
	cnopts = pysftp.CnOpts()
	cnopts.hostkeys = None
	srv = pysftp.Connection(
		host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
		username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
		password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
		cnopts=cnopts
	)
	return srv


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
		if srv.exists(filename):
			srv.remove(filename)
		if isinstance(mp3_file, str):
			file = open(mp3_file, 'rb')
			srv.putfo(file, filename)
			file.close()
		else:
			file = mp3_file
			file.seek(0)
			try:
				srv.putfo(file, filename)
			except FileNotFoundError as e:
				print(e)
				print(f'ERROR!! FILE NOT FOUND {filename} {path}')
				return False
	return True


PYTTX_FR_F_VOICE = 'Vocalizer Expressive Audrey Harpo 22kHz'
PYTTX_FR_M_VOICE = 'Vocalizer Expressive Thomas Harpo 22kHz'
PYTTX_RU_F_VOICE = 'Vocalizer Expressive Milena Harpo 22kHz'
PYTTX_RU_M_VOICE = 'Vocalizer Expressive Yuri Harpo 22kHz'
PYTTX_VOICES = {
	LANGUAGE_RU:{
		GENRE_MASCULINE:PYTTX_RU_M_VOICE,
		GENRE_FEMININE:PYTTX_RU_F_VOICE
	},
	LANGUAGE_FR:{
		GENRE_MASCULINE:PYTTX_FR_M_VOICE,
		GENRE_FEMININE:PYTTX_FR_F_VOICE
	}
}


def pytts_voice_string(s, filename, tag_id, tag_title, language=LANGUAGE_FR, genre=GENRE_FEMININE, ssml=False, verbs=False):
	import pyttsx3
	from pydub import AudioSegment
	filename = f'{filename}.mp3'
	temp_path_wav = 'le_francais_dictionary/local/temp/pytts_temp.wav'
	temp_path_mp3 = 'le_francais_dictionary/local/temp/pytts_temp.mp3'
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	voice_name = PYTTX_VOICES[language][genre]
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
	if ssml:
		s = s.replace('speak>', 'sapi>')
	else:
		s = f'<sapi>{s}</sapi>'
	engine.save_to_file(s, temp_path_wav)
	engine.runAndWait()
	wav_audio = AudioSegment.from_file(temp_path_wav, format='wav')
	wav_audio.export(temp_path_mp3, format='mp3')
	with open(temp_path_mp3, 'rb') as f:
		try:
			save_audio_stream_to_sftp(f.read(),
									  get_path(language, verbs),
									  filename,
									  tag_id,
									  tag_title,
									  voice_name, 'pyttsx3')
		except Exception as e:
			print(f'Error:\n'
				  f'{e}')
			return None
	return get_url_path(language, verbs) + filename


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)


def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False


def get_audio_links(words_list:List[Tuple[int, str, str]]):
	result = []
	for i, word, type_str in words_list:
		is_verb = False
		if type_str == 'v':
			is_verb = True
		url = get_url_path(language_code=LANGUAGE_FR, verbs=is_verb) + escape_non_url_characters(remove_parenthesis(word)) + '.mp3'
		if url_ok(url) and False:
			result.append((i, word, url))
			continue
		else:
			ftp_path = get_path(LANGUAGE_FR, is_verb)
			shtooka_url = shtooka_by_title_in_path(
				title=word,
				ftp_path=ftp_path,
				filename=unidecode(remove_parenthesis(word)),
				language_code=LANGUAGE_FR,
				genre=None,
				verbs=is_verb
			)
			if not shtooka_url:
				url = amazon_polly_tts(
					s=word,
					filename=escape_non_url_characters(remove_parenthesis(word)),
					language=LANGUAGE_FR,
					genre=GENRE_FEMININE,
					file_id=88888888,
					file_title=word,
					ftp_path=ftp_path,
					verbs=is_verb
				)
			else:
				url = shtooka_url
			result.append((i, word, url))
	return result


def fr_local_polly():
	CD_ID = 0
	STRING_FOR_SYNTH = 3
	FILENAME = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	import csv
	from .models import Word
	words = Word.objects.all()
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		print(i, end='\t')
		if i == 1:
			continue
		cd_id = int(row[CD_ID])
		word = next((w for w in words if w.cd_id == cd_id), None)
		if word:
			word.word_ssml = '<sapi>{txt}</sapi>'.format(txt=row[STRING_FOR_SYNTH])
			filename = unidecode(row[FILENAME])+'.mp3'
			word.create_polly_task(local=filename)
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_FR_F_VOICE
	else:
		voice_name = PYTTX_FR_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 3
	FILENAME_ROW = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR.csv'
	path = 'le_francais_dictionary/local/fr_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/fr_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	words = list(Word.objects.all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		word = next(
			(word for word in words if word.cd_id == cd_id), None)
		if word:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path + filename
			word._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/' + filename + '.mp3'
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if word.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = fr_engine_change_voice(engine, word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(string, wav_path + filename + '.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(path + filename + '.mp3', format='mp3')
			mp3 = eyed3.load(path + filename + '.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(word.word)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename + '.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def ru_engine_change_voice(engine, genre):
	if genre == GENRE_FEMININE:
		voice_name = PYTTX_RU_F_VOICE
	else:
		voice_name = PYTTX_RU_M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation
	import os
	import eyed3
	CD_ID_ROW = 0
	FILENAME_ROW = 5
	STRING_ROW = 3
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-RU.csv'
	path = 'le_francais_dictionary/local/ru_pyttsx3/'
	wav_path = 'le_francais_dictionary/local/ru_pyttsx3_wav/'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 150)
	engine.setProperty('volume', 0.8)
	translations = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[STRING_ROW]:
			print('!!!EMPTY_STRING!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		translation = next((tr for tr in translations if tr.word.cd_id == cd_id), None)
		if translation:
			filename = clean_filename(row[FILENAME_ROW])
			filepath = path+filename
			translation._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/RU/' + filename + '.mp3'
			to_update.append(translation)
			if os.path.exists(filepath+'.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			if translation.genre != GENRE_MASCULINE:
				print('!!!WRONG_GENRE!!!')
				continue
			engine, voice_name = ru_engine_change_voice(engine, translation.word.genre)
			string = '<sapi>' + row[STRING_ROW] + '</sapi>'
			engine.save_to_file(row[STRING_ROW], wav_path+filename+'.wav')
			engine.runAndWait()
			from pydub import AudioSegment
			wav_audio = AudioSegment.from_file(wav_path+filename+'.wav', format='wav')
			wav_audio.export(path+filename+'.mp3', format='mp3')
			mp3 = eyed3.load(path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = str(translation.translation)
			mp3.tag.artist = voice_name
			mp3.tag.album = 'pyttsx3'
			mp3.tag.save(encoding='utf-8')
			print(filename+'.mp3')
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])


def googletts_get_ru_voice(voices, genre):
	VOICE_MALE_NAME = 'ru-RU-Wavenet-B'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
	VOICE_NEUTRAL_NAME = 'ru-RU-Wavenet-D'
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def googletts_get_fr_voice(voices, genre):
	VOICE_MALE_NAME = 'fr-FR-Wavenet-D'
	VOICE_FEMALE_NAME = 'fr-FR-Wavenet-E'
	VOICE_NEUTRAL_NAME = VOICE_MALE_NAME
	if genre == GENRE_MASCULINE:
		voice_name = VOICE_MALE_NAME
	elif genre == GENRE_FEMININE:
		voice_name = VOICE_FEMALE_NAME
	else:
		voice_name = VOICE_NEUTRAL_NAME
	for voice in voices:
		if voice.name == voice_name:
			return voice


def local_fr_googletts(language='FR'):
	from google.cloud import texttospeech
	from le_francais_dictionary.models import Word, WordTranslation
	import csv
	import os
	import eyed3
	from pydub import AudioSegment
	voices_language_code = 'fr-FR' if language=='FR' else 'ru-RU'
	CD_ID_ROW_INDEX = 0
	STRING_ROW_INDEX = 3
	FILENAME_ROW_INDEX = 5
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-{0}.csv'.format(language)
	mp3_path = 'le_francais_dictionary/local/to_update_ftp_ru_m_gootle/'.format(language)
	wav_path = 'le_francais_dictionary/local/{0}_googletts_wav/'.format(language)
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices(language_code=voices_language_code).voices
	if language == 'FR':
		obj_list = list(Word.objects.all())
	else:
		obj_list = list(WordTranslation.objects.select_related('word').all())
	to_update = []
	csv_file = open(csv_path, 'r', encoding='utf-8')
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		cd_id = int(row[CD_ID_ROW_INDEX])
		filename = clean_filename(row[FILENAME_ROW_INDEX])
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = 'https://files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
			to_update.append(obj)
			if os.path.exists(mp3_path + filename + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
				continue
			string_to_synth = row[STRING_ROW_INDEX]
			if not string_to_synth:
				print('!!!EMPTY_STRING!!!')
				continue
			if '>' in string_to_synth:
				synthesis_input = texttospeech.types.SynthesisInput(
					ssml='<speak>{0}</speak>'.format(string_to_synth)
				)
			else:
				synthesis_input = texttospeech.types.SynthesisInput(
					text=string_to_synth
				)
			if language == 'FR':
				continue
				if obj.genre == GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre != GENRE_MASCULINE:
					print("!!!WRONG_GENRE!!!")
					continue
				voice = googletts_get_ru_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='ru-RU',
					name=voice.name,
				)
			audio_config = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
				speaking_rate=0.85 if language == 'FR' else 1,
			)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)
			with open(wav_path+filename+'.wav', 'wb') as out:
				out.write(response.audio_content)
				print(filename + '.mp3')
			wav_audio = AudioSegment.from_file(wav_path + filename + '.wav',
			                                   format='wav')
			wav_audio.export(mp3_path + filename + '.mp3', format='mp3', bitrate='128',)
			mp3 = eyed3.load(mp3_path+filename+'.mp3')
			mp3.tag.track_num = (str(cd_id), None)
			mp3.tag.title = obj.__str__()
			mp3.tag.artist = voice.name
			mp3.tag.album = 'Google Cloud TTS'
			mp3.tag.save(encoding='utf-8')


def local_copy_prerecorded():
	CD_ID_ROW = 0
	RU_ROW = 3
	RU_UNIFIED_ROW = 3
	FR_ROW = 2
	FR_UNIFIED_ROW = 3
	import os
	import csv
	from le_francais_dictionary.models import Word, UnifiedWord, WordTranslation
	words_list: List[Word] = list(Word.objects.select_related('group').all())
	translations_list: List[WordTranslation] = list(WordTranslation.objects.select_related('word').all())
	unified_words_list: List[UnifiedWord] = list(UnifiedWord.objects.select_related('group').all())
	csv_path = 'le_francais_dictionary/local/temp.csv'
	csv_file = open(csv_path, 'r', encoding='utf-8')
	ru_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/RU/'
	fr_url_dir = 'https://files.le-francais.ru/dictionnaires/sound/FR/'
	ru_dir = 'D:/Sound/RussianBX3/'
	fr_dir = 'D:/Sound/SoundF3/'
	ru_result_dir = 'le_francais_dictionary/local/ru_prerecorded/'
	fr_result_dir = 'le_francais_dictionary/local/fr_prerecorded/'
	to_update_words = []
	to_update_translations = []
	to_update_unified_words = []
	not_existing = set()
	for i, row in enumerate(csv.reader(csv_file), 1):
		if i == 1:
			continue
		print(i, end='\t')
		if not row[CD_ID_ROW]:
			print('!!EMPTY CD_ID!!!')
			continue
		cd_id = int(row[CD_ID_ROW])
		(
			filename_ru,
			filename_ru_unified,
			filename_fr,
			filename_fr_unified
		) = (
			row[RU_ROW],
			row[RU_UNIFIED_ROW],
			row[FR_ROW],
			row[FR_UNIFIED_ROW]
		)
		word: Word = next(
			(w for w in words_list if w.cd_id == cd_id), None)
		if word and filename_fr:
			word._polly_url = fr_url_dir + filename_fr.lower()
			group_id = word.group_id
			defenition_num = word.definition_num
			to_update_words.append(word)
			unified_word = next((uw for uw in unified_words_list if
			                     (uw.group_id == group_id and
			                      uw.definition_num == defenition_num)),
			                    None)
			if unified_word:
				unified_word.word_polly_url = fr_url_dir + filename_fr_unified
				unified_word.translation_polly_url = ru_url_dir + filename_ru_unified
				to_update_unified_words.append(unified_word)
		translation: WordTranslation = next((t for t in translations_list if t.word.cd_id == cd_id), None)
		if translation and filename_ru:
			translation._polly_url = ru_url_dir + filename_ru.lower()
			to_update_translations.append(translation)
		if (os.path.exists(ru_result_dir + filename_ru) and
				os.path.exists(fr_result_dir + filename_fr) and
				os.path.exists(ru_result_dir + filename_ru_unified) and
				os.path.exists(fr_result_dir + filename_fr_unified)):
			print('!!!FILES_ALREADY_EXISTS!!!')
			continue
		if filename_ru:
			if not copy_file(ru_dir+filename_ru, ru_result_dir+filename_ru):
				not_existing.add(filename_ru)
		if filename_ru_unified:
			if not copy_file(ru_dir + filename_ru_unified,
			                 ru_result_dir + filename_ru_unified):
				not_existing.add(filename_ru)
		if filename_fr:
			if not copy_file(fr_dir + filename_fr, fr_result_dir + filename_fr):
				not_existing.add(filename_fr)
		if filename_fr_unified:
			if not copy_file(fr_dir + filename_fr_unified,
			                 fr_result_dir + filename_fr_unified):
				not_existing.add(filename_fr_unified)
		print('Done!')
	from django_bulk_update import helper
	helper.bulk_update(to_update_words, update_fields=['_polly_url'])
	helper.bulk_update(to_update_translations, update_fields=['_polly_url'])
	helper.bulk_update(to_update_unified_words, update_fields=['translation_polly_url', 'word_polly_url'])
	print(not_existing)
