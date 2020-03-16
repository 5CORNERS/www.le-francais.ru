import os
from mutagen.mp3 import EasyMP3
import pysftp
from io import BytesIO

import eyed3
from google.cloud import texttospeech
from polly.api import PollyAPI
from polly.const import LANGUAGE_CODE_FR as LANGUAGE_FR, \
	LANGUAGE_CODE_RU as LANGUAGE_RU, VOICE_ID_LEA as POLLY_FR_VOICE_FEMALE, \
	VOICE_ID_MATHIEU as POLLY_FR_VOICE_MALE, TEXT_TYPE_SSML, TEXT_TYPE_TEXT, SAMPLE_RATE_22050, OUTPUT_FORMAT_MP3
from pydub import AudioSegment

from polly.models import PollyTask

fr_words = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/FR/'
fr_verbs = fr_words + 'verbs/'
fr_verbs_url = 'https://files.le-francais.ru/dictionnaires/sound/FR/verbs/'
ru_words = '/var/www/www-root/data/www/files.le-francais.ru/dictionnaires/sound/RU/'
ru_verbs = ru_words + 'verbs/'
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

def google_cloud_tts(s, filename, language=LANGUAGE_FR, genre=GENRE_FEMININE, file_id=None, file_title=None):
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
	save_to_sftp(response.audio_content, get_path(language), filename, file_id, file_title, voice.name, file_album='Google Cloud')
	return get_url_path(language) + filename + '.mp3'

def amazon_polly_tts(s, filename, language=LANGUAGE_FR, genre=GENRE_FEMININE, file_id=None, file_title=None):
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
	save_to_sftp(stream.read(), get_path(language), filename, file_id, file_title, voice_id, file_album='Amazon Polly')
	return get_url_path(language) + filename + '.mp3'


def save_to_sftp(audio_stream, path, filename, file_id, file_title,
                 file_author, file_album):
	with BytesIO() as mp3_file:
		mp3_file.write(audio_stream)
		mp3 = EasyMP3(mp3_file)
		mp3.add_tags()
		mp3['tracknumber'] = file_id
		mp3['title'] = file_title
		mp3['artist'] = file_author
		mp3['album'] = file_album
		mp3.save(mp3_file)
		cnopts = pysftp.CnOpts()
		cnopts.hostkeys = None
		srv = pysftp.Connection(
			host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
			username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
			password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
			cnopts=cnopts
		)
		with srv.cd(path):
			mp3_file.seek(0)
			srv.putfo(mp3_file, filename + '.mp3')
