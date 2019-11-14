import re
from datetime import datetime, timedelta
from typing import List

from unidecode import unidecode

from .consts import INITIAL_E_FACTOR, FIRST_REPETITION_DELTA, \
	SECOND_REPETITION_DELTA, GENRE_MASCULINE, GENRE_FEMININE


def create_or_update_repetition(user_word_data, save=False):
	from .models import UserWordRepetition
	repetition_datetime, time = user_word_data.get_repetition_datetime()
	if repetition_datetime:
		repetition, created = UserWordRepetition.objects.get_or_create(
			user_id=user_word_data.user_id,
			word_id=user_word_data.word_id,
		)
		repetition.time=time
		repetition.repetition_date = repetition_datetime.date()
		if save:
			repetition.save()
		return repetition
	return None


def sm2_response_quality(grade, mistakes):
	quality = 5
	if grade == 0:
		quality = 3
	if mistakes:
		quality = quality - mistakes
	return quality if quality > 0 else 1


def sm2_new_e_factor(response_quality:int, last_e_factor:float=None) -> float:
	last_e_factor = last_e_factor or INITIAL_E_FACTOR
	result = last_e_factor + (0.1-(5-response_quality)*(0.08+(5-response_quality)*0.02))
	if result < 1.3:
		result = 1.3
	return result


def sm2_next_repetition_date(dataset):
	e_factor = 2.5
	finals = []
	for user_data in sorted(dataset, key=lambda x: x.id, reverse=False):
		response_quality = sm2_response_quality(user_data.grade, user_data.mistakes)
		e_factor = sm2_new_e_factor(response_quality, e_factor)
		if user_data.grade == 1:
			finals.append((user_data, e_factor))
	if not finals:
		return None
	repetition_delta = 1
	for n, final in enumerate(finals, 1):
		if n == 1:
			repetition_delta = FIRST_REPETITION_DELTA
		elif n == 2:
			repetition_delta = SECOND_REPETITION_DELTA
		else:
			repetition_delta = repetition_delta * final[1]
	return finals[-1][0].datetime + timedelta(days=repetition_delta), n


def format_text2speech(text):
	# FIXME ignore double parentheses
	text = ''.join([s.split(')')[-1] for s in text.split('(')])  # ignore parentheses
	text = re.sub(' +', ' ', text)  # remove multiple whitespaces
	return text


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
			word._polly_url = '//files.le-francais.ru/dictionnaires/sound/fr/' + filename
			to_update.append(word)
	from django_bulk_update import helper
	helper.bulk_update(to_update, update_fields=['word_ssml', '_polly_url'])


def fr_engine_change_voice(engine, genre):
	F_VOICE = 'Vocalizer Expressive Audrey Harpo 22kHz'
	M_VOICE = 'Vocalizer Expressive Thomas Harpo 22kHz'
	if genre == GENRE_FEMININE:
		voice_name = F_VOICE
	else:
		voice_name = M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name


def fr_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation, Word
	import os
	import eyed3
	CD_ID_ROW = 0
	STRING_ROW = 1
	FILENAME_ROW = 2
	csv_path = 'le_francais_dictionary/local/Dictionary updated - SYNTH-FR_HOM.csv'
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
			filename = row[FILENAME_ROW]
			filepath = path + filename
			word._polly_url = '//files.le-francais.ru/dictionnaires/sound/FR/' + filename
			to_update.append(word)
			if os.path.exists(filepath + '.mp3'):
				print('!!!ALREADY_EXIST!!!')
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
	F_VOICE = 'Vocalizer Expressive Milena Harpo 22kHz'
	M_VOICE = 'Vocalizer Expressive Yuri Harpo 22kHz'
	if genre == GENRE_FEMININE:
		voice_name = F_VOICE
	else:
		voice_name = M_VOICE
	for voice in engine.getProperty('voices'):
		if voice.name == voice_name:
			engine.setProperty('voice', voice.id)
			return engine, voice_name

def ru_local_pyttsx3():
	import csv
	import pyttsx3
	from .models import WordTranslation, Word
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
			filename = row[FILENAME_ROW]
			filepath = path+filename
			translation._polly_url = '//files.le-francais.ru/dictionnaires/sound/RU/' + filename
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
	VOICE_MALE_NAME = 'ru-RU-Wavenet-D'
	VOICE_FEMALE_NAME = 'ru-RU-Wavenet-A'
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
	mp3_path = 'le_francais_dictionary/local/{0}_googletts/'.format(language)
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
		filename = row[FILENAME_ROW_INDEX]
		obj = next((obj for obj in obj_list if obj.cd_id==cd_id), None)
		if obj:
			obj._polly_url = '//files.le-francais.ru/dictionnaires/sound/{0}/'.format(language) + filename + '.mp3'
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
				voice = googletts_get_fr_voice(voices, obj.genre)
				voice = texttospeech.types.VoiceSelectionParams(
					language_code='fr-FR',
					name = voice.name,
				)
			elif language == 'RU':
				if obj.genre == GENRE_MASCULINE:
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
	from bulk_update import helper
	helper.bulk_update(to_update, update_fields=['_polly_url'])

