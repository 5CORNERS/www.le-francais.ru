import json
import traceback
from typing import List

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Subquery, OuterRef, \
    IntegerField
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, \
    HttpResponseNotFound, HttpResponseRedirect

# Create your views here.
from le_francais_dictionary.forms import WordsManagementFilterForm
from .consts import TENSE_PARTICIPE_PASSE, STAR_CHOICES
from .models import Word, Packet, UserPacket, \
    UserWordData, UserWordRepetition, UserWordIgnore, \
    UserStandalonePacket, \
    prefetch_words_data, VerbPacket, UserDayRepetition, get_repetition_words_query, VerbPacketRelation, \
    DictionaryError
from . import consts
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
                message=consts.PACKET_DOES_NOT_EXIST_MESSAGE,
                code=consts.PACKET_DOES_NOT_EXIST_CODE,
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
                            message=consts.NO_CUPS_MESSAGE,
                            code=consts.NO_CUPS_MESSAGE
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
                    message=consts.LESSON_IS_NOT_ACTIVATED_MESSAGE,
                    code=consts.LESSON_IS_NOT_ACTIVATED_CODE
                ))
        else:
            result['errors'].append(dict(
                packet=packet.pk,
                message=consts.USER_IS_NOT_AUTHENTICATED_MESSAGE,
                code=consts.USER_IS_NOT_AUTHENTICATED_CODE,
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
    packet_id = int(packet_id)
    if packet_id == 99999999:
        standalone_packet = UserStandalonePacket.objects.get(user=request.user)
        words = Word.objects.filter(pk__in=standalone_packet.words)
        words = prefetch_words_data(words, request.user)
        result['words'] = [word.to_dict(user=request.user) for word in words]
    else:
        try:
            packet = Packet.objects.prefetch_related(
                'word_set', 'word_set__polly',
                'wordtranslation_set',
                'wordtranslation_set__polly', 'lesson').get(pk=packet_id)
            if packet.demo or packet.is_activated(request.user):
                words = packet.word_set.select_related('packet').order_by('order')
                if request.user.is_authenticated:
                    words = list(words.exclude(
                    userwordignore__user=request.user))
                    if not words:
                        result['errors'].append({
                            'message':consts.ALL_WORDS_ARE_IGNORED_MESSAGE,
                            'code':consts.ALL_WORDS_ARE_IGNORED_CODE,
                        })
                result['words'] = [word.to_dict(user=request.user) for word in words]
            elif not request.user.is_authenticated:
                result['errors'].append(
                    dict(
                        message=consts.USER_IS_NOT_AUTHENTICATED_MESSAGE,
                        code=consts.USER_IS_NOT_AUTHENTICATED_CODE,
                    )
                )
            elif (not packet.demo
                  and not packet.is_activated(request.user)):
                result['errors'].append(
                    dict(
                        message=consts.LESSON_IS_NOT_ACTIVATED_MESSAGE,
                        code=consts.LESSON_IS_NOT_ACTIVATED_CODE,
                    )
                )

        except Packet.DoesNotExist:
            result['errors'].append(
                dict(
                    message=consts.PACKET_DOES_NOT_EXIST_MESSAGE,
                    code=consts.PACKET_DOES_NOT_EXIST_CODE,
                )
            )
        except Exception as e:
            result['errors'].append(dict(
                message=f'Unknown Error: {e.__doc__}',
                code=consts.UNKNOWN_ERROR_CODE
            ))
    return JsonResponse(result, safe=False)


def get_repetition_words(request):
    result = {
        'words': [],
        'errors': [],
    }
    if request.user.is_authenticated:
        words = get_repetition_words_query(request.user)
        words = prefetch_words_data(list(words), user=request.user)
        for i, word in reversed(list(enumerate(words))):
            if word.get_repetition(request.user) and word.get_repetition(request.user).repetition_datetime > timezone.now():
                words.pop(i)
        result['words'] = [
            word.to_dict() for word in words
        ]
    else:
        result['errors'].append(dict(
            message=consts.USER_IS_NOT_AUTHENTICATED_REPETITIONS_MESSAGE,
            code=consts.USER_IS_NOT_AUTHENTICATED_CODE,
        ))

    if not result['words']:
        result['errors'].append(
            {
                'code': consts.NO_REPETITION_WORDS_CODE,
                'message': consts.NO_REPETITION_WORDS_MESSAGE,
            }
        )

    return JsonResponse(result, safe=False)


@csrf_exempt
def update_words(request):
    try:
        data = json.loads(request.body)
        if isinstance(data, dict):
            words_data: List[dict] = data.get('words', [])
        else:
            # FIXME return error if wrong json format
            words_data: List[dict] = []
        user_words_data: List[UserWordData] = []
        errors = []
        for word_data in words_data:
            try:
                word = Word.objects.select_related('packet').get(pk=word_data['pk'])
                if word.group is not None:
                    new_word = Word.objects.filter(
                        userdata__user=request.user, group=word.group
                    ).order_by('-userwordrepetition__time').distinct()
                    if new_word.exists() and new_word.first() != word:
                        word = new_word.first()
                grade = word_data.get('grade', None)
                mistakes = word_data.get('mistakes', None)
                if mistakes < 0:
                    mistakes = None
                delay = word_data.get('delay', None)
                if delay < 0:
                    delay = None
                custom_grade = word_data.get('customGrade', None)
                if not isinstance(custom_grade, int) or not 0 <= custom_grade <= 5:
                    custom_grade = None
                if word.packet.demo or word.packet.is_activated(request.user):
                    user_words_data.append(UserWordData(
                        word=word,
                        user_id=request.user.id,
                        grade=grade,
                        mistakes=mistakes,
                        delay=delay,
                        custom_grade=custom_grade,
                        timezone=request.user.timezone
                    ))
                else:
                    errors.append(dict(
                        pk=word.pk,
                        message=consts.LESSON_IS_NOT_ACTIVATED_MESSAGE,
                        code=consts.LESSON_IS_NOT_ACTIVATED_CODE,
                    ))
            except Word.DoesNotExist:
                errors.append(dict(
                    pk=word_data['pk'],
                    message=consts.WORD_DOES_NOT_EXIST_MESSAGE,
                    code=consts.WORD_DOES_NOT_EXIST_CODE,
                ))
                DictionaryError.objects.create(
                    user=request.user,
                    message=f'Error while update word: {consts.WORD_DOES_NOT_EXIST_CODE}\n'
                            f'{consts.WORD_DOES_NOT_EXIST_MESSAGE}\n'
                            f'Word ID: {word_data["pk"]}\n'
                            f'\n==================\n'
                            f'{traceback.format_exc()}'
                            f'\n==================\n'
                )
            except Exception as e:
                errors.append(dict(
                    pk=word_data['pk'],
                    message=f'Unknown Error: {e}',
                    code = consts.UNKNOWN_ERROR_CODE,
                ))
                DictionaryError.objects.create(
                    user=request.user,
                    message=f'Uknown Error while update\n'
                            f'\n==================\n'
                            f'{traceback.format_exc()}'
                            f'\n==================\n'
                )
        user_words_data = UserWordData.objects.bulk_create(user_words_data)
        words = []
        for user_word_data in user_words_data:
            e_factor = user_word_data.e_factor
            quality = user_word_data.quality
            mean_quality = user_word_data.mean_quality # FIXME returns -1
            delay = user_word_data.delay

            repetition = user_word_data.update_or_create_repetition()
            if repetition:
                repetition_datetime = repetition.repetition_datetime
                repetition_time = repetition.time
            else:
                repetition_datetime = None
                repetition_time = None

            words.append(dict(
                pk=user_word_data.word_id,
                grade=user_word_data.grade,
                customGrade=user_word_data.custom_grade,
                delay=delay,
                quality=quality,
                nextRepetition=repetition_datetime,
                repetitionTime=repetition_time,
                eFactor=e_factor,
                meanQuality=mean_quality,
                history=[dict(
                    datetime=d.datetime,
                    grade=d.grade,
                    userGrade=d.custom_grade,
                    delay=d.delay,
                    quality=d.quality,
                    nextRepetition=d.sm2_word_data.next_repetition,
                    repetitionTime=d.sm2_word_data.repetition_time,
                    eFactor=d.e_factor,
                    meanQuality=d.mean_quality
                ) for d in user_word_data.user_word_dataset]
            ))
        return JsonResponse(dict(words=words, errors=errors), safe=False)
    except Exception as e:
        create_dictionary_error(request)
        raise e


def create_dictionary_error(request):
    DictionaryError.objects.create(
        user=request.user if request.user.is_authenticated else None,
        message=f'Fatal Error while Updating Words:\n'
                f'REQUEST DATA:\n'
                f'method: {request.method}\n'
                f'body:\n'
                f'==============\n'
                f'{request.body}\n'
                f'==============\n'
                f'user:{request.user}\n'
                f'GET PARAMS:\n'
                f'==============\n'
                f'{request.GET}\n'
                f'==============\n'
                f'POST PARAMS:\n'
                f'==============\n'
                f'{request.POST}\n'
                f'==============\n'
                f'TRACEBACK:\n'
                f'==================\n'
                f'{traceback.format_exc()}'
                f'==================\n'
    )


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
    if int(pk) == 99999999:
        try:
            packet = UserStandalonePacket.objects.get(user=request.user)
            if packet.words is None:
                packet.words = Packet.objects.get(lesson__lesson_number=1).word_set.all().values_list('pk', flat=True)
            result = packet.to_dict(user=request.user)
            result['isAuthenticated'] = request.user.is_authenticated
        except UserStandalonePacket.DoesNotExist:
            result = {
                "pk": 99999999,
                "name": "Пользовательский пакет",
                "lessonNumber": None,
                "demo": True,
                "activated": True,
                "added": True,
                "wordsCount": 0,
                "isAuthenticated": True
            }
        return JsonResponse(result)
    try:
        result = Packet.objects.get(pk=pk).to_dict(user=request.user)
        result['isAuthenticated'] = request.user.is_authenticated
        return JsonResponse(result)
    except Packet.DoesNotExist:
        return HttpResponseNotFound(consts.PACKET_DOES_NOT_EXIST_MESSAGE)


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
                    repetitions = UserWordRepetition.objects.filter(word=word, user=request.user)
                    user_day_repetitions = UserDayRepetition.objects.filter(repetitions__overlap=[r.pk for r in repetitions])
                    for user_day_repetition in user_day_repetitions:
                        changed = False
                        for i, r_pk in reversed(list(enumerate(user_day_repetition.repetitions))):
                            if r_pk in [r.pk for r in repetitions]:
                                user_day_repetition.repetitions.pop(i)
                                changed = True
                        if changed:
                            user_day_repetition.save()
            except Word.DoesNotExist:
                result['errors'].append(
                    dict(
                        pk=pk,
                        message=consts.WORD_DOES_NOT_EXIST_MESSAGE,
                        code=consts.WORD_DOES_NOT_EXIST_CODE
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
                message=consts.USER_IS_NOT_AUTHENTICATED_MESSAGE,
                code=consts.USER_IS_NOT_AUTHENTICATED_CODE,
            )
        )
    return JsonResponse(result, safe=False)

@csrf_exempt
def unmark_words(request):
    data = json.loads(request.body)
    result = {'unmarked': [], 'errors': []}
    if request.user.is_authenticated:
        for pk in data['words']:
            try:
                word = Word.objects.get(pk=pk)
                if UserWordIgnore.objects.filter(
                        user=request.user, word_id=pk).exists():
                    UserWordIgnore.objects.get(
                        user=request.user,
                        word=word,
                    ).delete()
                    result['unmarked'].append(pk)
            except Word.DoesNotExist:
                result['errors'].append(
                    dict(
                        pk=pk,
                        message=consts.WORD_DOES_NOT_EXIST_MESSAGE,
                        code=consts.WORD_DOES_NOT_EXIST_CODE
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
                message=consts.USER_IS_NOT_AUTHENTICATED_MESSAGE,
                code=consts.USER_IS_NOT_AUTHENTICATED_CODE,
            )
        )
    return JsonResponse(result, safe=False)


def get_app(request, packet_id):
    if not UserPacket.objects.filter(user=request.user,
                                     packet_id=packet_id).exists():
        UserPacket.objects.create(
            user=request.user,
            packet_id=packet_id
        )
    return render(request, 'dictionary/dictionary_app.html',
                      {'packet_id': packet_id, 'mode': 'learn'})


class ManageWords(View):
    def post(self, request):
        form = WordsManagementFilterForm(request.user, request.POST)
        table = form.table_dict()
        table_html = render_to_string('dictionary/words_table.html',
                                      {'table': table}, request)
        if request.is_ajax():
            return JsonResponse(
                {'table': table_html, 'errors': form.errors},
                safe=False)
        else:
            return self.get(request)

    @method_decorator(login_required)
    def get(self, request):
        # TODO: podcasts support
        form = WordsManagementFilterForm(request.user)
        init_packets = None
        init_lesson = request.GET.get('lesson', None)
        init_packet = request.GET.get('lesson_pk', None)
        if init_lesson is not None:
            try:
                init_lesson = int(init_lesson)
                init_packets = Packet.objects.filter(
                    lesson__lesson_number=init_lesson).values_list(
                    'pk', flat=True)
            except ValueError:
                init_packets = None
        elif init_packet is not None:
            if init_packet == '99999999':
                return HttpResponseRedirect(
                    redirect_to=f'{reverse("dictionary:my_words")}?last=true'
                )
            try:
                init_packet = int(init_packet)
                if init_packet == 88888888:
                    init_packets = [88888888]
                else:
                    init_packets = Packet.objects.filter(
                        pk=init_packet).values_list('pk', flat=True)
            except ValueError:
                init_packets = None
        table = form.table_dict()

        return render(request, 'dictionary/manage_words.html',
                      {'form': form, 'table': table,
                       'star_choices': STAR_CHOICES,
                       'init_packets': init_packets})

@csrf_exempt
@login_required
def start_app(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data['words']
        standalone_packet, created = UserStandalonePacket.objects.get_or_create(user=request.user)
        standalone_packet.words = [int(pk) for pk in ids]
        standalone_packet.save()
        return JsonResponse({'message': 'OK'}, status=200)
    else:
        return render(request, 'dictionary/dictionary_app_standalone.html', {
	        'packet_id': 99999999,
	        'mode': 'learn'
        })


def start_app_repeat(request):
	return render(request, 'dictionary/dictionary_app_standalone.html', {
		'packet_id': 99999999,
		'mode': 'repeat'
	})


def get_verbs(request, packet_id:int, more_lessons:int=None):
    if more_lessons is not None:
        more_lessons = int(more_lessons)
    result = {
        "user": {},
        "verbs": [],
        "errors": [],
        # "isInfinitiveTranslation":None,
    }
    try:
        packet = VerbPacket.objects.get(pk=packet_id)
        # result['isInfinitiveTranslation'] = int(packet.lesson.lesson_number) % 2 == 0
    except VerbPacket.DoesNotExist:
        result['errors'].append({
            "message": consts.PACKET_DOES_NOT_EXIST_MESSAGE,
            "code": consts.PACKET_DOES_NOT_EXIST_CODE,
        })
        return JsonResponse(result, status=404)
    if more_lessons:
        current_lesson = packet.lesson.lesson_number
        more_packets = list(VerbPacket.objects.filter(
            lesson__lesson_number__gte=current_lesson - more_lessons,
            lesson__lesson_number__lt=current_lesson
        ).order_by('-lesson__lesson_number'))
        for packet in [packet] + more_packets:
            result['verbs'] = result['verbs'] + packet.to_dict()
    else:
        result['verbs'] = packet.to_dict()
    activated_lessons_pks = []
    tenses = list(set(verb['tense'] for verb in result['verbs']))
    if request.user.is_authenticated:
        activated_lessons_pks = UserLesson.objects.filter(
            user=request.user).values_list('lesson__pk', flat=True)
    packets = VerbPacket.objects.annotate(
        num_verbs=Subquery(
            VerbPacketRelation.objects.filter(packet=OuterRef('pk'))
                .exclude(tense=TENSE_PARTICIPE_PASSE)
                .values('packet').annotate(count=Count('pk')).values(
                'count')),
        num_participes=Subquery(
            VerbPacketRelation.objects.filter(packet=OuterRef('pk'),
                                              tense=TENSE_PARTICIPE_PASSE)
                .values('packet').annotate(count=Count('pk')).values(
                'count'), output_field=IntegerField())
    ).prefetch_related('lesson').all().order_by(
        'lesson__lesson_number')
    result['packets'] = [{
        'id': p.id,
        'lessonNumber': p.lesson.lesson_number,
        'verbsCount': p.num_verbs,
        'participesCount': p.num_participes,
        'activated': p.lesson.pk in activated_lessons_pks,
    } for p in packets]
    result['verbListHTML'] = ""
    return JsonResponse(result, status=200)


def get_repetition_words_count(request):
    if request.user.is_anonymous:
        result = {
            'count': 0
        }
    else:
        words = get_repetition_words_query(request.user)
        result = {
            'count': words.count()
        }
    return JsonResponse(result, status=200)

@csrf_exempt
def get_filters(request):
    user = request.user
    try:
        userpacket= UserStandalonePacket.objects.get(user=user)
    except UserStandalonePacket.DoesNotExist:
        return HttpResponseNotFound()
    if userpacket.filters is None:
        return HttpResponseNotFound()
    return JsonResponse(
        userpacket.filters, status=200
    )

@csrf_exempt
def save_filters(request):
    data = json.loads(request.body)
    filters = data['filters']
    userpacket, created = UserStandalonePacket.objects.get_or_create(user=request.user)
    userpacket.filters = filters
    userpacket.save()
    return HttpResponse(status=200)


def manage_words_standalone(request, lesson_number):
    star_choices = STAR_CHOICES
    form = WordsManagementFilterForm(request.user)
    init_lesson = int(lesson_number)
    init_packets = Packet.objects.filter(
        lesson__lesson_number=init_lesson).values_list(
        'pk', flat=True)
    return render(request, 'dictionary/manage_words_standalone.html',
                  {'form': form, 'table': form.table_dict(),
                   'star_choices': star_choices,
                   'init_packets': init_packets})
