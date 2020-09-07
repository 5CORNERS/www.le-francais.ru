import re
import statistics
from datetime import datetime, timedelta
from typing import List, Optional, Any

import pytz
from django.utils import timezone
from unidecode import unidecode

from .consts import INITIAL_E_FACTOR, FIRST_REPETITION_DELTA, \
	SECOND_REPETITION_DELTA, GENRE_MASCULINE, GENRE_FEMININE


def create_or_update_repetition(user_id, word_id, repetition_datetime, time):
	from .models import UserDayRepetition
	from .models import UserWordRepetition
	repetition, repetition_created = UserWordRepetition.objects.get_or_create(
		user_id=user_id,
		word_id=word_id,
	)
	repetition.repetition_datetime = repetition_datetime
	repetition.time = time
	repetition.save()
	if not repetition_created:
		for old_day_repetitions in UserDayRepetition.objects.filter(
				repetitions__contains=[repetition.pk]):
			old_day_repetitions.repetitions.remove(repetition.pk)
			old_day_repetitions.save()
	if repetition.time < 5:
		day_repetitions, day_repetition_created = UserDayRepetition.objects.get_or_create(
			user_id=user_id,
			datetime=repetition_datetime
		)
		if day_repetition_created:
			day_repetitions.repetitions = []
		if (day_repetitions.repetitions is None or
				not repetition.pk in day_repetitions.repetitions):
			day_repetitions.repetitions.append(repetition.pk)
		if not day_repetition_created:
			to_remove = list(UserWordRepetition.objects.filter(
				pk__in=day_repetitions.repetitions
			).exclude(
				repetition_datetime__exact=repetition_datetime
			).exclude(pk=repetition.pk).distinct().values_list('pk',
			                                                   flat=True))
			if to_remove:
				day_repetitions.repetitions = [
					x for x in day_repetitions.repetitions if
					x not in to_remove
				]
		day_repetitions.save()
	return repetition



def message(n, form1='новое слово', form2='новых слова', form5='новых слов'):
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return '{0} {1}'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return '{0} {1}'.format(str(n), form2)
    else:
        return '{0} {1}'.format(str(n), form5)



def mistakes_grade(mistakes, word):
	ratio = word.mistake_ratio(mistakes)
	if ratio == 0:
		return 0
	elif ratio < 0.4:
		return 1
	elif ratio < 0.7:
		return 2
	else:
		return 3

def sm2_response_quality(data, zeros_dataset):
	q = 5
	mistakes = data.mistakes - data.word.unrelated_mistakes
	if zeros_dataset.__len__() >= 2:
		q = 0
	elif zeros_dataset.__len__() == 1:
		q = 2
	q = q - mistakes_grade(mistakes, data.word)
	return q if q > 0 else 0




def sm2_new_e_factor(response_quality:int, last_e_factor:float=None) -> float:
	last_e_factor = last_e_factor or INITIAL_E_FACTOR
	result = last_e_factor + (0.1-(5-response_quality)*(0.08+(5-response_quality)*0.02))
	if result < 1.3:
		result = 1.3
	elif result > 2.5:
		result = 2.5
	return result


def sm2_ef_q_mq(dataset) -> (float, int, float):
	"""
	Returns final e_factor, quality and mean quality for given user_data set
	:param dataset: list of UserData objects
	"""
	e_factor = 2.5
	finals = []
	qualities = []
	zeros_dataset = []
	for data in sorted(dataset, key=lambda x: x.datetime, reverse=False):
		if data.grade:
			response_quality = sm2_response_quality(data, zeros_dataset)
			qualities.append(response_quality)
			e_factor = sm2_new_e_factor(response_quality, e_factor)
			if response_quality < 3:
				finals = []
			finals.append((data, e_factor, response_quality))
			zeros_dataset = []
		else:
			zeros_dataset.append(data)
	if not finals:
		return None, None, None
	return finals[-1][1], finals[-1][2], statistics.mean(qualities)


def sm2_next_repetition_date(dataset):
	e_factor = 2.5
	finals = []
	zeros_dataset = []
	for data in sorted(dataset, key=lambda x: x.datetime, reverse=False):
		if data.grade:
			response_quality = sm2_response_quality(data, zeros_dataset)
			e_factor = sm2_new_e_factor(response_quality, e_factor)
			zeros_dataset = []
			if response_quality < 3:
				finals = []
			finals.append((data, e_factor, response_quality))
		else:
			zeros_dataset.append(data)
	if not finals:
		return None, None
	repetition_delta = 1
	for n, final in enumerate(finals, 0):
		if n == 0:
			repetition_delta = FIRST_REPETITION_DELTA
		elif n == 1:
			repetition_delta = SECOND_REPETITION_DELTA
		else:
			repetition_delta = repetition_delta * final[1]
	return finals[-1][0].datetime + timedelta(days=repetition_delta), n


def format_text2speech(text):
	# FIXME ignore double parentheses
	text = ''.join([s.split(')')[-1] for s in text.split('(')])  # ignore parentheses
	text = re.sub(' +', ' ', text)  # remove multiple whitespaces
	return text


def clean_filename(filename:str):
	return filename.strip(' ').strip(' ').replace(' ', '_').replace('__', '_').replace('*', '')


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
	from bulk_update import helper
	# helper.bulk_update(to_update, update_fields=['_polly_url'])


import os
from shutil import copyfile
def copy_file(src, dest):
	if os.path.exists(dest):
		return True
	elif not os.path.exists(src):
		return False
	else:
		copyfile(src, dest.lower())
		return True


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
