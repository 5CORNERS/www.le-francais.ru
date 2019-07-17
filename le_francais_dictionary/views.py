import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from home.models import LessonPage
from le_francais_dictionary.models import Word


def get_words(request, lesson_number):
	words = Word.objects.prefetch_related(
		'wordtranslation_set',
		'wordtranslation_set__polly',
		'polly').order_by('cd_id').filter(lessons=LessonPage.objects.get(lesson_number=lesson_number))
	words = [word.to_dict() for word in words]
	return JsonResponse({'words': words}, safe=False)
