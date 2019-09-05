import json
from typing import List

from bulk_update.helper import bulk_update
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.
from le_francais_dictionary.models import Word, UserWord
from home.models import UserLesson


# TODO: write get_calendar function
def get_calendar(request):
	...


# TODO: write function get_progress
def get_progress(request):
	user = request.user
	user_lessons = UserLesson.objects.annotate().filter(user=user)


# TODO: packet id instead of lesson_number
def get_words(request, lesson_number):
	lesson_number = int(lesson_number)
	words = Word.objects.prefetch_related(
		'wordtranslation_set',
		'wordtranslation_set__polly',
		'polly',
	).order_by('pk').filter(packet__lesson__lesson_number=lesson_number)
	words_dict = [word.to_dict() for word in words]
	return JsonResponse({'words': words_dict}, safe=False)


def get_user_words(request):
	words = Word.objects.prefetch_related(
		'wordtranslation_set',
		'wordtranslation_set__polly',
		'polly',
	).order_by('pk').filter(
		userword__user=request.user
	)
	result = dict(
		words=[word.to_dict(with_user=True, user=request.user) for word in words]
	)
	return JsonResponse(result)


@csrf_exempt
def add_packets(request):
	data = json.loads(request.body)


# TODO: change to add_packets
@csrf_exempt
def add_user_words(request):
	pks = json.loads(request.body)['words']
	already = list(UserWord.objects.filter(word_id__in=pks, user=request.user).values_list('word_id', flat=True).order_by('id'))
	to_create = [UserWord(
			user=request.user,
			word_id=pk,
			update_datetime=timezone.now(),
			stars=0
		) for pk in pks]
	to_create = list(filter(lambda a: not a.word_id in already, to_create))
	UserWord.objects.bulk_create(to_create)
	result = dict(
		created=[w.word_id for w in to_create],
		alreadyExist=already,
	)
	return JsonResponse(result)

# TODO: new grade system
@csrf_exempt
def update_user_words(request):
	new_user_words = json.loads(request.body)['words']
	new_user_words = {uw['pk']: {'stars':uw['stars']} for uw in new_user_words}
	user_words: List[UserWord] = list(UserWord.objects.filter(
		word_id__in=new_user_words.keys(), user=request.user))
	for uw in user_words:
		uw.stars = new_user_words[uw.word_id].get('stars')
		uw.update_datetime = timezone.now()
	bulk_update(user_words, update_fields=['stars', 'update_datetime'])
	result = dict(
		updated=[uw.word_id for uw in user_words]
	)
	return JsonResponse(result)


