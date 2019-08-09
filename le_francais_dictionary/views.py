from django.http import JsonResponse, HttpResponse
from rest_framework import serializers

# Create your views here.
from le_francais_dictionary.models import Word, WordUser


def get_words(request, lesson_number):
	lesson_number = int(lesson_number)
	words = Word.objects.prefetch_related(
		'wordtranslation_set',
		'wordtranslation_set__polly',
		'polly',
		'lessons'
	).order_by('pk').filter(
		lessons__lesson_number__in=list(range(lesson_number+1))[-6:])
	words_dict = [word.to_dict() for word in words]
	if request.user.is_authenticated:
		user_words = WordUser.objects.filter(
			word__in=words,
			user=request.user
		)
		user_words_dict = [user_word.to_dict() for user_word in user_words]
	else:
		user_words_dict = None
	return JsonResponse({'words': words_dict, 'user_words': user_words_dict}, safe=False)


def get_words_alt(request, lesson_number):
	lesson_number = int(lesson_number)
	from django.core import serializers
	words = Word.objects.prefetch_related(
		'wordtranslation_set',
		'wordtranslation_set__polly',
		'polly',
		'lessons'
	).order_by('pk').filter(lessons__lesson_number__in=list(range(lesson_number+1))[-6:])
	data = serializers.serialize('json', words)
	return HttpResponse(data, content_type='application/json')


def push_changes(request):
	user = request.user
	words = Word.json_to_query(request.POST.get('words'))

	Word.objects.bulk_update(words, exclude_fields=['pk'])
