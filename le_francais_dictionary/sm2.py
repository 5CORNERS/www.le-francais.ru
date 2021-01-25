import statistics
from datetime import datetime, timedelta
from typing import Union, Tuple, List

from numpy import inf, mean


class WordSM2:

	def __init__(self, dataset):
		self.dataset = sorted(dataset, key=lambda x: x.datetime)
		self.e_factor = None
		self.last_quality = None
		self.mean_quality = None
		self.next_repetition = None
		self.repetition_time = None
		self.sm2_next_repetition_date()

	def sm2_next_repetition_date(self) -> None:
		zeros_dataset = []
		repetitions_datetimes: List[datetime] = []
		answers_datetimes: List[datetime] = []
		qualities_list = []
		n = 0
		e_factor = 2.5
		for data in self.dataset:
			answer_datetime = data.datetime

			answer_quality = sm2_response_quality(data, zeros_dataset)

			if data.grade:
				zeros_dataset = []
				qualities_list.append(answer_quality)
			else:
				zeros_dataset.append(data)

			new_repetition_date = None

			new_e_factor = sm2_new_e_factor(answer_quality, e_factor)

			if answer_quality >= 3:
				if n == 0:
					new_repetition_date = answer_datetime + timedelta(
						days=1)
				else:
					# дата предыдущего повторения
					last_repetition_date = answers_datetimes[-1]
					# дата следующего (текущего) повторения
					current_repetition_date = repetitions_datetimes[-1]
					# дельта между текущим ответом и датой предыдущего повторения
					current_answer_delta = answer_datetime - last_repetition_date
					# дельта между предыдущим и следующим (текущим) повторением
					current_repetition_delta = current_repetition_date - last_repetition_date

					if answer_datetime > current_repetition_date:
						if n == 1:
							new_repetition_date = answer_datetime + timedelta(
								days=2)
						else:
							new_repetition_date = answer_datetime + timedelta(
								days=current_repetition_delta.days * new_e_factor)
					else:
						current_next_ratio = current_answer_delta / current_repetition_delta
						new_e_factor = e_factor + (
									new_e_factor - e_factor) * current_next_ratio
						if n == 1:
							pass
						else:
							# новая персчитанная дата повторения
							new_current_repetition_date = last_repetition_date + timedelta(
								days=current_repetition_delta.days * new_e_factor)
							if new_current_repetition_date < answer_datetime:
								# если новая дата повторения оказывается раньше следующего
								# засчитываем текущий ответ как после следующего повторения
								repetitions_datetimes[
									-1] = new_current_repetition_date
								new_repetition_date = answer_datetime + timedelta(
									days=current_repetition_delta * new_e_factor)
							else:
								# иначе отодвигаем дату повторения
								# и не засчитываем ответ
								repetitions_datetimes[
									-1] = new_current_repetition_date

			else:
				# при оценке <= 2 сбрасываем цикл повторений
				# и назначаем следующее повторение на завтра
				n = 0
				repetitions_datetimes = []
				answers_datetimes = []
				new_repetition_date = answer_datetime + timedelta(days=1)

			if new_repetition_date is not None:
				repetitions_datetimes.append(new_repetition_date)
				answers_datetimes.append(answer_datetime)
				if data.grade:
					e_factor = new_e_factor
				n += 1

		self.e_factor = e_factor
		self.mean_quality = mean(qualities_list)
		self.last_quality = qualities_list[-1]
		if repetitions_datetimes:
			self.next_repetition = repetitions_datetimes[-1]
			self.repetition_time = n


def mistakes_grade_obsolete(mistakes, word):
	ratio = word.mistake_ratio(mistakes)
	if ratio == 0:
		return 0
	elif ratio < 0.4:
		return 1
	elif ratio < 0.7:
		return 2
	else:
		return 3


def sm2_response_quality_obsolete(data, zeros_dataset):
	q = 5
	mistakes = data.mistakes - data.word.unrelated_mistakes
	if zeros_dataset.__len__() >= 2:
		q = 0
	elif zeros_dataset.__len__() == 1:
		q = 2
	q = q - mistakes_grade_obsolete(mistakes, data.word)
	return q if q > 0 else 0


def mistakes_grade(mistakes, word):
	ratio = word.mistake_ratio(mistakes)
	if ratio == 0:
		return 0
	elif ratio < 0.5:
		return -3
	else:
		return -4


def sm2_response_quality(data, zeros_dataset):
	q: int = 5
	mistakes = data.mistakes - data.word.unrelated_mistakes
	delay = data.delay
	if data.custom_grade and isinstance(data.custom_grade, int) and 0 <= data.custom_grade <= 5:
		q = data.custom_grade
	elif zeros_dataset and data.grade:
		q = 0
	elif delay and not mistakes and data.grade:
		for delay_start, delay_end, delay_minus in DELAY_RANGES:
			if delay_start <= delay <= delay_end:
				q += delay_minus
				break
	elif mistakes and data.grade:
		q += mistakes_grade(mistakes, data.word)
	elif data.grade and delay is None:
		q = sm2_response_quality_obsolete(data, zeros_dataset)
	elif not data.grade:
		q = 0
	return q if q > 0 else 0


def sm2_new_e_factor(response_quality: int,
                     last_e_factor: float = None) -> float:
	last_e_factor = last_e_factor or INITIAL_E_FACTOR
	result = last_e_factor + (0.1 - (5 - response_quality) * (
				0.08 + (5 - response_quality) * 0.02))
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
	for data in sorted(dataset, key=lambda x: x.datetime,
	                   reverse=False):
		if data.grade:
			response_quality = sm2_response_quality(data,
			                                        zeros_dataset)
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


def sm2_next_repetition_date_obsolete(dataset) -> Union[
	Tuple[datetime, int], Tuple[None, None]]:
	"""
	:param dataset: List of UserWordData objects for one user
	:return: Datetime and repetition count or None, None
	"""
	e_factor = 2.5
	finals = []
	zeros_dataset = []
	for data in sorted(dataset, key=lambda x: x.datetime,
	                   reverse=False):
		if data.grade:
			response_quality = sm2_response_quality(data,
			                                        zeros_dataset)
			e_factor = sm2_new_e_factor(response_quality, e_factor)
			zeros_dataset = []
			if response_quality <= 2:
				finals = []
			finals.append((data, e_factor, response_quality))
		else:
			zeros_dataset.append(data)
	if not finals:
		return None, None
	repetition_delta = 1
	n = 0
	for n, final in enumerate(finals, 0):
		if n == 0:
			repetition_delta = FIRST_REPETITION_DELTA
		elif n == 1:
			repetition_delta = SECOND_REPETITION_DELTA
		else:
			repetition_delta = repetition_delta * final[1]
	return finals[-1][0].datetime + timedelta(
		days=repetition_delta), n


DELAY_RANGE_MINUS_1 = (0, 5000, 0)
DELAY_RANGE_MINUS_2 = (5001, 10000, -1)
DELAY_RANGE_MINUS_3 = (10001, 20000, -2)
DELAY_RANGE_MINUS_5 = (20001, inf, -5)
DELAY_RANGES = [DELAY_RANGE_MINUS_1, DELAY_RANGE_MINUS_2,
                DELAY_RANGE_MINUS_3, DELAY_RANGE_MINUS_5]
INITIAL_E_FACTOR = 2.5
FIRST_REPETITION_DELTA = 1
SECOND_REPETITION_DELTA = 6
