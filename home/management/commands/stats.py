from django.core.management import BaseCommand

from custom_user.models import LogMessage
from home.models import UserLesson, LessonPage

def run():
	user_lesson_activation_map = {}
	for user_lesson in UserLesson.objects.prefetch_related(
			'lesson').all().order_by('date'):
		user_lesson_activation_map[
			f'{user_lesson.user_id}_{user_lesson.lesson.lesson_number}'] = user_lesson

	result = []
	first_users_ids = []
	for lesson in LessonPage.objects.all().order_by('lesson_number'):
		first_users_count = 0
		users_count = 0
		frequency = 0

		datetimes = []
		for user_lesson, activation in user_lesson_activation_map.items():
			user_id, lesson_number = user_lesson.split('_')

			if int(lesson_number) == lesson.lesson_number:
				if user_id not in first_users_ids:
					first_users_count += 1
					first_users_ids.append(user_id)
				users_count += 1
				datetimes.append(activation.date)



		result.append({'lesson': lesson.lesson_number,
		               'first_activations': first_users_count,
		               'activations': users_count})

	print('lesson\tfirst_activations\tall_activations')
	for row in result:
		print(
			f"{row['lesson']}\t{row['first_activations']}\t{row['activations']}")

def freebies():
	lesson_payed_dict = {}
	lesson_free_dict = {}
	lesson_general_dict = {}
	user_lesson_activation_map = {}
	for user_lesson in UserLesson.objects.prefetch_related(
			'lesson').all().order_by('date'):
		user_lesson_activation_map[
			f'{user_lesson.user_id}_{user_lesson.lesson.lesson_number}'] = user_lesson
	for log_message in LogMessage.objects.filter(user__isnull=False):
		if f'{log_message.user_id}_{log_message.message}' in user_lesson_activation_map.keys():
			if not int(log_message.message) in lesson_payed_dict.keys():
				lesson_payed_dict[int(log_message.message)] = 0
			lesson_payed_dict[int(log_message.message)] += 1
		else:
			if not int(log_message.message) in lesson_free_dict.keys():
				lesson_free_dict[int(log_message.message)] = 0
			lesson_free_dict[int(log_message.message)] += 1
	for log_message in LogMessage.objects.all():
		if not int(log_message.message) in lesson_general_dict.keys():
			lesson_general_dict[int(log_message.message)] = 0
		lesson_general_dict[int(log_message.message)] += 1
	print('lesson\tpayees\tfrees\tall')
	for lesson in LessonPage.objects.all().order_by('lesson_number'):
		lesson_number = lesson.lesson_number
		lesson_payed = 0
		lesson_free = 0
		lesson_all = 0
		if lesson_number in lesson_payed_dict.keys():
			lesson_payed = lesson_payed_dict[lesson_number]
		if lesson_number in lesson_free_dict.keys():
			lesson_free = lesson_free_dict[lesson_number]
		if lesson_number in lesson_general_dict.keys():
			lesson_all = lesson_general_dict[lesson_number]
		print(f'{lesson_number}\t{lesson_payed}\t{lesson_free}\t{lesson_all}')

class Command(BaseCommand):
	def handle(self, *args, **options):
		freebies()
