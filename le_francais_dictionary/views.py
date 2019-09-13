import json
from typing import List

from bulk_update.helper import bulk_update
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.
from le_francais_dictionary.models import Word, Packet, UserPacket, \
	UserWordData
from home.models import UserLesson


# TODO: write get_calendar function
def get_calendar(request):
	...


@csrf_exempt
def add_packets(request):
	pks = json.loads(request.body)['packets']
	packets = list(Packet.objects.filter(id__in=pks))
	added = []
	already_exist = []
	for packet in packets:
		usr_packet, created = UserPacket.objects.get_or_create(packet=packet, user=request.user)
		if created:
			added.append(usr_packet)
		else:
			already_exist.append(usr_packet)
	return JsonResponse(data=dict(
		added=[packet.pk for packet in added],
		already_exist=[packet.pk for packet in already_exist]
	))





def get_progress(request):
	last_lesson_number = request.user.latest_lesson_number
	packets:List[Packet] = Packet.objects.filter(
		Q(lesson__lesson_number__lte=last_lesson_number if last_lesson_number is not None and last_lesson_number > 10 else 10)|Q(
			userpacket__user=request.user
		)
	)
	activated_lessons = list(request.user.payed_lessons.all().values_list('id', flat=True))
	added_packets = Packet.objects.filter(userpacket__user=request.user).values_list('id', flat=True)
	packets_data = []
	for packet in packets:
		packets_data.append(dict(
			pk=packet.pk,
			name=packet.name,
			activated=True if packet.lesson_id in activated_lessons else False,
			added=True if packet.pk in added_packets else False,
			wordsCount=packet.words_count,
			wordsLearned=Word.objects.filter(userdata__user=request.user, userdata__grade=1, packet=packet).count()
		))
	return JsonResponse({'packets': packets_data})


def get_words(request, packet_id):
	words = Word.objects.prefetch_related(
		'wordtranslation_set',
		'wordtranslation_set__polly',
		'polly',
	).order_by('pk').filter(packet_id=packet_id)
	words_dict = [word.to_dict() for word in words]
	return JsonResponse({'words': words_dict}, safe=False)

def update_words(request):
	words_data = json.loads(request.body)['words']
	user_words:List[UserWordData] = []
	for word in words_data:
		user_words.append(UserWordData(
			word_id=word['pk'],
			user_id=request.user.id,
			grade=word['grade'],
			mistakes=word['mistakes'],
		))
	user_words = UserWordData.objects.bulk_create(user_words)
	result = []
	for user_word in user_words:
		result.append(dict(
			pk=user_word.word_id,
			nextRepetition=user_word.get_next_repetition_datetime()
		))
	return JsonResponse(result, safe=False)
