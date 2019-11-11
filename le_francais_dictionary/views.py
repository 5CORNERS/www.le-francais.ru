import json
from typing import List
from bulk_update.helper import bulk_update
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound

from django.utils.translation import ugettext_lazy as _

# Create your views here.
from .models import Word, Packet, UserPacket, \
    UserWordData, UserWordRepetition, UserWordIgnore
from .utils import create_or_update_repetition
from .consts import PACKET_IS_NOT_ADDED_MESSAGE, \
    PACKET_DOES_NOT_EXIST_MESSAGE, LESSON_IS_NOT_ACTIVATED_MESSAGE, \
    USER_IS_NOT_AUTHENTICATED_MESSAGE, WORD_DOES_NOT_EXIST_MESSAGE, \
    TOO_EARLY_MESSAGE, NO_LEFT_CUPS_MESSAGE
from home.models import UserLesson


# TODO: write get_calendar function
def get_calendar(request):
    ...


@csrf_exempt
def add_packets(request):
    data = json.loads(request.body)
    pks = data['packets']
    packets = []
    result = {'added': [], 'already_exist': [], 'errors': []}
    for pk in pks:
        try:
            packets.append(Packet.objects.get(pk=pk))
        except Packet.DoesNotExist:
            result['errors'].append(dict(
                packet=pk,
                message=PACKET_DOES_NOT_EXIST_MESSAGE
            ))
    for packet in packets:
        if request.user.is_authenticated:
            if 'activate' in data.keys() and data['activate']:
                if not packet.lesson.payed(request.user):
                    cups_amount = packet.lesson.add_lesson_to_user(
                        request.user)
                    if not cups_amount:
                        result['errors'].append(dict(
                            packet=packet.pk,
                            message=NO_LEFT_CUPS_MESSAGE,
                        ))
                        result['coffee_amount'] = 0
                    result['coffee_amount'] = cups_amount
            if (packet.lesson.payed(request.user) or
                    packet.demo):
                usr_packet, created = UserPacket.objects.get_or_create(
                    packet=packet,
                    user=request.user
                )
                if created:
                    result['added'].append(usr_packet.packet_id)
                else:
                    result['already_exist'].append(usr_packet.packet_id)
            else:
                result['errors'].append(dict(
                    packet=packet.pk,
                    message=LESSON_IS_NOT_ACTIVATED_MESSAGE
                ))
        else:
            result['errors'].append(dict(
                packet=packet.pk,
                message=USER_IS_NOT_AUTHENTICATED_MESSAGE,
            ))
    return JsonResponse(result)


def get_progress(request):
    # FIXME prefetch related objects
    result = {'isAuthenticated': request.user.is_authenticated, 'packets': []}
    packets = Packet.objects.prefetch_related(
        'lesson__paid_users',
        'userpacket_set',
        'word_set',
    ).all().order_by('lesson__lesson_number')
    for packet in packets:
        result['packets'].append(packet.to_dict(user=request.user))
    return JsonResponse(result)


def get_words(request, packet_id):
    result = {
        'words': [],
        'errors': [],
    }
    try:
        packet = Packet.objects.prefetch_related(
            'words', 'words__polly',
            'words__wordtranslation_set',
            'words__wordtranslation_set__polly').get(pk=packet_id)
        if (packet.demo or (
                request.user.is_authenticated and
                packet.userpacket_set.filter(user=request.user))):
            words = packet.words.order_by('pk')
            if request.user.is_authenticated:
                words = words.exclude(
                userwordignore__user=request.user)
            result['words'] = [word.to_dict(user=request.user, packet=packet) for word in words]
        elif not request.user.is_authenticated:
            result['errors'].append(
                dict(
                    message=USER_IS_NOT_AUTHENTICATED_MESSAGE
                )
            )
        elif (not packet.demo
              and not packet.userpacket_set.filter(user=request.user)):
            result['errors'].append(
                dict(
                    message=PACKET_IS_NOT_ADDED_MESSAGE
                )
            )

    except Packet.DoesNotExist:
        result['errors'].append(
            dict(
                message=PACKET_DOES_NOT_EXIST_MESSAGE
            )
        )
    return JsonResponse(result, safe=False)


def get_repetition_words(request):
    result = {
        'words': [],
        'errors': [],
    }
    if request.user.is_authenticated:
        repetitions = UserWordRepetition.objects.prefetch_related(
            'word',
            'word__wordtranslation_set',
            'word__wordtranslation_set__polly',
            'word__polly').filter(
            repetition_date__lte=timezone.now(), user=request.user).exclude(
            word__userwordignore__user=request.user
        )
        result['words'] = [
            repetition.word.to_dict(user=request.user) for repetition in repetitions
        ]
    else:
        result['errors'].append(dict(
            message=USER_IS_NOT_AUTHENTICATED_MESSAGE
        ))

    return JsonResponse(result, safe=False)


@csrf_exempt
def update_words(request):
    words_data = json.loads(request.body)['words']
    user_words_data: List[UserWordData] = []
    errors = []
    for word_data in words_data:
        try:
            word = Word.objects.get(pk=word_data['pk'])
            grade = word_data['grade']
            mistakes = word_data['mistakes']
            if UserWordRepetition.objects.filter(
                    word=word, user=request.user,
                    repetition_date__gt=timezone.now()):
                errors.append(dict(
                    pk=word.pk,
                    message=TOO_EARLY_MESSAGE)
                )
            elif word.packets.filter(userpacket__user=request.user).exists():
                user_words_data.append(UserWordData(
                    word=word,
                    user_id=request.user.id,
                    grade=grade,
                    mistakes=mistakes,
                ))
            else:
                errors.append(dict(
                    pk=word.pk,
                    message=PACKET_IS_NOT_ADDED_MESSAGE
                ))
        except Word.DoesNotExist:
            errors.append(dict(
                pk=word_data['pk'],
                message=WORD_DOES_NOT_EXIST_MESSAGE
            ))
    user_words_data = UserWordData.objects.bulk_create(user_words_data)
    words = []
    repetitions = []
    for user_word_data in user_words_data:
        if user_word_data.grade:
            repetition = create_or_update_repetition(user_word_data)
            repetition_datetime = repetition.repetition_date
            repetition_time = repetition.time
            repetitions.append(repetition)
        else:
            repetition_datetime = None
            repetition_time = None
        words.append(dict(
            pk=user_word_data.word_id,
            nextRepetition=repetition_datetime,
            repetitionTime=repetition_time
        ))
    bulk_update(repetitions, update_fields=['repetition_date'])
    return JsonResponse(dict(words=words, errors=errors), safe=False)


def clear_all(request):
    result = ''
    packets_deleted = UserPacket.objects.filter(user=request.user).delete()
    result += str(packets_deleted) + '\n'
    data_deleted = UserWordData.objects.filter(user=request.user).delete()
    result += str(data_deleted) + '\n'
    repetetions_deleted = UserWordRepetition.objects.filter(user=request.user).delete()
    result += str(repetetions_deleted) + '\n'
    ignores_deleted = UserWordIgnore.objects.filter(user=request.user).delete()
    result += str(ignores_deleted) + '\n'
    return HttpResponse(status=200, content=result)


def get_packet_progress(request, pk):
    try:
        result = Packet.objects.get(pk=pk).to_dict(user=request.user)
        result['isAuthenticated'] = request.user.is_authenticated
        return JsonResponse(result)
    except Packet.DoesNotExist:
        return HttpResponseNotFound(PACKET_DOES_NOT_EXIST_MESSAGE)


@csrf_exempt
def mark_words(request):
    data = json.loads(request.body)
    result = {'marked': [], 'errors': []}
    if request.user.is_authenticated:
        for pk in data['words']:
            try:
                word = Word.objects.get(pk=pk)
                if not UserWordIgnore.objects.filter(
                        user=request.user, word_id=pk).exists():
                    UserWordIgnore.objects.create(
                        user=request.user,
                        word=word,
                    )
                    result['marked'].append(pk)
            except Word.DoesNotExist:
                result['errors'].append(
                    dict(
                        pk=pk,
                        message=WORD_DOES_NOT_EXIST_MESSAGE,
                    )
                )
            except ValidationError as e:
                for message in e.messages:
                    result['errors'].append(
                        dict(
                            pk=pk,
                            message=message
                        )
                    )

    else:
        result['errors'].append(
            dict(
                message=USER_IS_NOT_AUTHENTICATED_MESSAGE
            )
        )
    return JsonResponse(result, safe=False)
