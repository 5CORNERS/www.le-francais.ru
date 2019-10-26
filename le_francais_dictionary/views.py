import json
from typing import List
from bulk_update.helper import bulk_update
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

# Create your views here.
from .models import Word, Packet, UserPacket, \
    UserWordData, UserWordRepetition
from .utils import create_repetition
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
        usr_packet, created = UserPacket.objects.get_or_create(packet=packet,
                                                               user=request.user)
        if created:
            added.append(usr_packet)
        else:
            already_exist.append(usr_packet)
    return JsonResponse(data=dict(
        added=[packet.pk for packet in added],
        already_exist=[packet.pk for packet in already_exist]
    ))


def get_progress(request):
    packets = Packet.objects.prefetch_related('lesson__paid_users', 'userpacket_set').all().order_by('lesson__lesson_number')
    packets_data = []
    for packet in packets:
        packets_data.append(packet.to_dict(user=request.user))
    return JsonResponse({'packets': packets_data})


def get_words(request, packet_id):
    words = Word.objects.prefetch_related(
        'wordtranslation_set',
        'wordtranslation_set__polly',
        'polly',
    ).order_by('pk').filter(packet_id=packet_id)
    words_dict = [word.to_dict() for word in words]
    return JsonResponse({'words': words_dict}, safe=False)


def get_repetition_words(request):
    repetitions = UserWordRepetition.objects.prefetch_related(
        'word',
        'word__wordtranslation_set',
        'word__wordtranslation_set__polly',
        'word__polly').filter(
        repetition_date__lte=timezone.now())
    word_dict = [repetition.word.to_dict() for repetition in repetitions]
    return JsonResponse({'words': word_dict}, safe=False)


def update_words(request):
    words_data = json.loads(request.body)['words']
    user_words_data: List[UserWordData] = []
    for word in words_data:
        user_words_data.append(UserWordData(
            word_id=word['pk'],
            user_id=request.user.id,
            grade=word['grade'],
            mistakes=word['mistakes'],
        ))
    user_words_data = UserWordData.objects.bulk_create(user_words_data)
    result = []
    repetitions = []
    for user_word_data in user_words_data:
        if user_word_data.grade:
            repetition = create_repetition(user_word_data)
            repetition_datetime = repetition.repetition_date
            repetition_time = repetition.time
            repetitions.append(repetition)
        else:
            repetition_datetime = None
            repetition_time = None
        result.append(dict(
            pk=user_word_data.word_id,
            nextRepetition=repetition_datetime,
            repetitionTime=repetition_time
        ))
    bulk_update(repetitions, update_fields=['repetition_date'])
    return JsonResponse(result, safe=False)


def clear_all(request):
    result = ''
    for user_packet in UserPacket.objects.filter(user=request.user):
        packets_deleted = user_packet.delete()
        result += str(packets_deleted) + '\n'
    for user_data in UserWordData.objects.filter(user=request.user):
        data_deleted = user_data.delete()
        result += str(data_deleted) + '\n'
    for user_repetition in UserWordRepetition.objects.filter(user=request.user):
        repetetions_deleted = user_repetition.delete()
        result += str(repetetions_deleted) + '\n'
    return HttpResponse(status=200, content=result)
