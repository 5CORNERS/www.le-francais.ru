import json
import os
from pathlib import Path

from mutagen.mp3 import EasyMP3, HeaderNotFoundError
from io import BytesIO

from unidecode import unidecode

from le_francais_dictionary.consts import GENRE_MASCULINE, \
	GENRE_FEMININE

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

def google_cloud_tts(s, filename, language=LANGUAGE_FR, genre=GENRE_FEMININE, file_id=None, file_title=None, ftp_path=None, speacking_rate=None, ssml=False):
	if check_if_file_exists(filename+'.mp3', ftp_path or get_path(language)):
		return get_url_path(language) + filename + '.mp3'
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
		speaking_rate=speacking_rate or 0.9,
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
	return get_url_path(language) + filename


def shtooka_by_title_in_path(title, ftp_path, filename=None, language_code=LANGUAGE_FR, genre=GENRE_FEMININE):
	title = unidecode(title).lower().strip()
	path = os.environ.get('SHTOOKA_PATH', None)
	second_path = os.environ.get('SHTOOKA_PATH_SECOND', None)
	if path is None:
		return None
	titles_map = get_titles_map(path)
	titles_map_second = get_titles_map(second_path)

	if title in titles_map.keys():
		mp3_filename = titles_map[title]
		if genre == GENRE_FEMININE and not 'fem' in filename:
			if check_if_file_exists(filename, ftp_path or get_path()):
				delete_ftp_file(filename, ftp_path or get_path())
			return None
		if not filename:
			filename = mp3_filename
		else:
			filename = filename+f'.{mp3_filename.split(".")[-1]}'
		put_to_ftp(filename,
				   f'{path}/{mp3_filename}',
				   ftp_path or get_path(language_code))
		# TODO fix different paths to return
		return f'https://files.le-francais.ru/dictionnaires/sound/FR/{filename}'
	elif title in titles_map_second.keys():
		mp3_filename = titles_map_second[title]
		if genre == GENRE_FEMININE and not 'fem' in filename:
			if check_if_file_exists(filename, ftp_path or get_path()):
				delete_ftp_file(filename, ftp_path or get_path())
			return None
		if not filename:
			filename = mp3_filename
		else:
			filename = filename+f'.{mp3_filename.split(".")[-1]}'
		put_to_ftp(filename, f'{second_path}/{mp3_filename}',
				   ftp_path or get_path(language_code))
		# TODO fix different paths to return
		return f'https://files.le-francais.ru/dictionnaires/sound/FR/{filename}'
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
	return titles_map


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
