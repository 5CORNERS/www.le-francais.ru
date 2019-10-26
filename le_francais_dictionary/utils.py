import re
from datetime import datetime, timedelta
from typing import List


from .consts import INITIAL_E_FACTOR, FIRST_REPETITION_DELTA, SECOND_REPETITION_DELTA


def create_repetition(user_word_data, save=False):
	from .models import UserWordRepetition
	repetition_datetime, time = user_word_data.get_repetition_datetime()
	if repetition_datetime:
		repetition, created = UserWordRepetition.objects.get_or_create(
			user_id=user_word_data.user_id,
			word_id=user_word_data.word_id,
			time=time
		)
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


def ignore_whitespaces(text):
	text = ''.join([s.split(')')[-1] for s in text.split('(')])  # ignore parentheses
	text = re.sub(' +', ' ', text)  # remove multiple whitespaces
	return text
