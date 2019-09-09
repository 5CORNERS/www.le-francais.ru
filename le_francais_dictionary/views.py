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
	user = request.user
	user_packets = list(UserPacket.objects.select_related('packet').filter(user=user).annotate(
		words_count=Count('packet__word'),
	))
	packets_data = []
	for user_packet in user_packets:
		packets_data.append(dict(
			pk=user_packet.packet_id,
			name=user_packet.packet.name,
			activated=True,
			added=True,
			wordsCount=user_packet.words_count,
			wordsLearned=UserWordData.objects.filter(grade=1, user=user, word__packet=user_packet.packet).count()
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

def update_user_words(request):
	...
