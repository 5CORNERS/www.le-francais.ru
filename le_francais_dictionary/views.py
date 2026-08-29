import json
import traceback
from json import JSONDecodeError
from typing import List
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Subquery, OuterRef, \
    IntegerField, Q, ProtectedError
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, \
    HttpResponseNotFound, HttpResponseRedirect

# Create your views here.
from le_francais_dictionary.forms import WordsManagementFilterForm, \
    VerbsManagementFilterForm
from .consts import TENSE_PARTICIPE_PASSE, STAR_CHOICES, WORD_JSON_FIELDS_TO_PYTHON, TRANSLATION_JSON_FIELDS_TO_PYTHON
from .models import Word, Packet, UserPacket, \
    UserWordData, UserWordRepetition, UserWordIgnore, \
    UserStandalonePacket, \
    prefetch_words_data, VerbPacket, UserDayRepetition, \
    get_repetition_words_query, VerbPacketRelation, \
    DictionaryError, verb_to_packet_relations_to_dict, WordTranslation, Partner
from . import consts
from home.models import UserLesson

User = get_user_model()


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

    packets = list(
        Packet.objects.select_related('lesson').all().order_by(
            'lesson__lesson_number'))
    user = request.user

    payed_lessons = []
    learned_words = []
    checked_words = []
    if user.is_authenticated:
        if user.must_pay:
            payed_lessons = user.payed_lessons.all()
        learned_words = Word.objects.filter(
            Q(userdata__user=user, userdata__grade=1) | Q(
                userwordignore__user=user
            )).values('word', 'packet_id').distinct()
        checked_words = Word.objects.filter(
            Q(userdata__user=user) | Q(userwordignore__user=user)
        ).values('word', 'packet_id').distinct()

    for packet in packets:
        if user.is_authenticated and packet.lesson is not None:
            if user.must_pay:
                packet.lesson._users_payed[user.pk] = packet.lesson in payed_lessons
            else:
                packet.lesson._users_payed[user.pk] = True
        packet._user_words_learned[user.pk] = sum(word['packet_id'] == packet.pk for word in learned_words)
        packet._user_words_checked[user.pk] = sum(word['packet_id'] == packet.pk for word in checked_words)

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
    if request.user.is_authenticated and not UserPacket.objects.filter(
            user=request.user, packet_id=packet_id).exists():
        UserPacket.objects.create(
            user=request.user,
            packet_id=packet_id
        )
    return render(request, 'dictionary/dictionary_app.html',
                      {'packet_id': packet_id, 'mode': 'learn'})


class ManageWords(View):
    def post(self, request):
        form = WordsManagementFilterForm(request.user, None, request.POST)
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
        form = WordsManagementFilterForm(request.user, cross_site=request.POST.get('ck', None))
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
                       'init_packets': init_packets,
                       'init_cross_site': request.POST.get('ck', None)
                       })


class ManageVerbs(View):
    @method_decorator(login_required)
    def get(self, request):
        form = VerbsManagementFilterForm(request.user)
        return render(request, 'dictionary/manage_verbs.html', {
            'form': form, 'table': form.table_dict()
        })

    def post(self, request):
        form = VerbsManagementFilterForm(request.user, request.POST)
        table = form.table_dict()
        table_html = render_to_string('dictionary/verbs_table.html',
                                      {'table':table}, request)
        if request.is_ajax():
            return JsonResponse({'table': table_html, 'errors': form.errors}, safe=False)
        else:
            return self.get(request)

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
            lesson__isnull=False,
            lesson__lesson_number__gte=current_lesson - more_lessons,
            lesson__lesson_number__lt=current_lesson
        ).order_by('-lesson__lesson_number'))
        for packet in [packet] + more_packets:
            result['verbs'] = result['verbs'] + packet.to_dict()
    else:
        result['verbs'] = packet.to_dict()
    attach_info(request, result)
    return JsonResponse(result, status=200)


def attach_info(request, result):
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
    ).prefetch_related('lesson').filter(lesson__isnull=False).order_by(
        'lesson__lesson_number')
    result['packets'] = [{
        'id': p.id,
        'lessonNumber': p.lesson.lesson_number,
        'verbsCount': p.num_verbs,
        'participesCount': p.num_participes,
        'activated': p.lesson.pk in activated_lessons_pks,
    } for p in packets]
    result['verbListHTML'] = ""
    return result


def get_repetition_words_count(request):
    if request.user.is_anonymous:
        result = {
            'count': 0
        }
    else:
        words = Word.objects.filter(
            userwordrepetition__repetition_datetime__lte=timezone.now(),
            userwordrepetition__user=request.user,
            userwordrepetition__time__lt=5
        ).exclude(userwordignore__user=request.user).values('cd_id').distinct()
        result = {
            'count': words.count()
        }
    return JsonResponse(result, status=200)


@csrf_exempt
def get_filters(request):
    user = request.user
    data = json.loads(request.body)
    filter_key = data.get('filterKey', "main")
    try:
        userpacket = UserStandalonePacket.objects.get(user=user)
    except UserStandalonePacket.DoesNotExist:
        return HttpResponseNotFound()

    filters = userpacket.filters_v2.get(filter_key, userpacket.filters_v2.get("main"))

    if filters is None:
        return HttpResponseNotFound()

    return JsonResponse(
        filters, status=200
    )


@csrf_exempt
def save_filters(request):
    data = json.loads(request.body)
    filter_key = data.get('filterKey', "main")
    filters = data['filters']

    userpacket, created = UserStandalonePacket.objects.get_or_create(user=request.user)

    if not isinstance(userpacket.filters_v2, dict):
        userpacket.filters_v2 = {}

    userpacket.filters_v2[filter_key] = filters
    userpacket.save(update_fields=['filters_v2'])

    return HttpResponse(status=200)


_courses_public_key = None


def load_courses_public_key():
    global _courses_public_key
    if _courses_public_key is None:
        with open('courses_public.pem', 'r') as key_file:
            _courses_public_key = key_file.read()
    return _courses_public_key


def manage_words_standalone(request, lesson_number):
    token = request.GET.get('token')
    if token:
        import jwt
        from django.contrib.auth import login
        try:
            public_key = load_courses_public_key()
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                issuer='courses.le-francais.ru',
                audience='www.le-francais.ru'
            )
            user_id = payload.get('user_id')
            if user_id:
                user = User.objects.get(pk=user_id)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        except Exception:
            pass

    star_choices = STAR_CHOICES
    init_lesson = int(lesson_number)
    if init_lesson != 0:
        template_name = 'dictionary/manage_words_standalone.html'
        init_packets = Packet.objects.filter(
            lesson__lesson_number=init_lesson).values_list(
            'pk', flat=True)
        cross_site_key = None
    else:
        template_name = 'dictionary/manage_words_iframe.html'
        packets_ids = list(map(lambda x: int(x), request.GET.getlist('p')))
        cross_site_key = request.GET.get('ck', None)
        init_packets = list(Packet.objects.filter(pk__in=packets_ids).values_list('pk', flat=True))
        if 88888888 in packets_ids:
            init_packets = [88888888] + init_packets
        if 99999999 in packets_ids:
            query_params = request.GET.copy()
            query_params['last'] = 'true'
            del query_params['p']
            return HttpResponseRedirect(
                f"{request.path}?{query_params.urlencode()}",
            )
        if not init_packets:
            init_packets = None
    form = WordsManagementFilterForm(request.user, cross_site=cross_site_key)
    return render(request, template_name,
                  {'form': form, 'table': form.table_dict(),
                   'star_choices': star_choices,
                   'init_packets': init_packets,
                   'cross_site_key': cross_site_key,
                   'init_cross_site': cross_site_key,
                   })


def open_verbs_iframe(request, packet_id):
    relations = VerbPacketRelation.objects.filter(packet__pk=packet_id).values_list('pk', flat=True)
    query_params = {
        'iframe': 'True'
    }
    if relations:
        query_params['v'] = relations
    url = f"{reverse('dictionary:app_verbs')}?{urlencode(query_params, doseq=True)}"
    return redirect(url)


def start_app_verbs(request):
    query = VerbPacketRelation.objects.filter(
        pk__in=map(int, request.GET.getlist('v')))
    data = {
        "user": {},
        "verbs": verb_to_packet_relations_to_dict(query),
        "errors": [],
    }
    data = attach_info(request, data)
    if request.GET.get('iframe', 'False') == 'True':
        template_name = 'dictionary/verbs_app_iframe.html'
    else:
        template_name = 'dictionary/verbs_app_standalone.html'
    return render(request, template_name, {'data': json.dumps(data)})


@csrf_exempt
def cross_site_packet(request):
    try:
        data = json.loads(request.body)
        if data['key'] not in settings.DICTIONARY_CROSS_SITE_KEYS.keys():
            return JsonResponse({'success': False, 'message':'Wrong key'}, status=403)

        site_name = settings.DICTIONARY_CROSS_SITE_KEYS[data['key']]
        partner, created = Partner.objects.get_or_create(
            name=data['partner']['name']
        )

        if request.method == 'GET':
            packet = Packet.objects.get(
                cross_site_id=data['id']
            )
        elif request.method == 'POST':
            packet, created = Packet.objects.get_or_create(
                cross_site_id=data['id']
            )
            packet.name = data['name']
            packet.partner = partner
            packet.cross_site_available=True
            packet.cross_site_id=data['id']
            packet.cross_site_site_name=site_name
            packet.save()
        elif request.method == 'DELETE':
            packet = Packet.objects.get(
                cross_site_id=data['id'], partner=partner
            )
            words = packet.word_set.all()
            try:
                words.delete()
                packet.delete()
            except ProtectedError as e:
                return JsonResponse({'success': False, 'message': f'Cannot delete packet. {e}'}, status=403)
        else:
            return HttpResponse('Method not allowed', status=405)
        return JsonResponse(packet.to_dict())

    except JSONDecodeError:
        return JsonResponse({'success':False, 'message':'JSONDecodeError'}, status=400)
    except Packet.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Packet not found'}, status=404)


def cross_site_words(request):
    try:
        data = json.loads(request.body)
        if data['key'] not in settings.DICTIONARY_CROSS_SITE_KEYS.keys():
            return JsonResponse({'success': False, 'message': 'Wrong key'}, status=403)
        site_name = settings.DICTIONARY_CROSS_SITE_KEYS[data['key']]
        partner = Partner.objects.get(name=data['partner']['name'])

        if request.method == 'GET':
            ...
    finally:
        pass


def get_partner_data(reqeust):
    data = json.loads(reqeust.body)
    try:
        partner = Partner.objects.get(name=data['name'])
    except Partner.DoesNotExist:
        return HttpResponseNotFound()
    return JsonResponse(partner.to_dict())


@csrf_exempt
def create_cross_site_words(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            return HttpResponse('JSONDecodeError', status=400)
        if data['key'] not in settings.DICTIONARY_CROSS_SITE_KEYS.keys():
            return HttpResponse('Wrong key', status=403)
        else:
            site_name = settings.DICTIONARY_CROSS_SITE_KEYS[data['key']]

        partner_name = data['partner']['name']
        partner = Partner.objects.get(name=partner_name)

        packet, created = Packet.objects.get_or_create(
            cross_site_id=data['table']['id'],
            partner=partner,
        )
        packet.name = data['table']['name']
        packet.cross_site_available=True
        packet.save()

        packet_words_ids = list(packet.word_set.all().values_list('cd_id', flat=True))
        saved_words_ids = []

        result = dict(
            success=False,
            packet=dict(
                id=packet.id,
                name=packet.name
            ),
            words=[],
            translations=[],
            errors=[], deleted=[], notDeleted=[]
        )

        for counter, card_data in enumerate(data['cards']):
            try:
                word = Word.objects.get(
                    cross_site_available=True,
                    cross_site_id=card_data['id'],
                    cross_site_site_name=site_name
                )
            except Word.DoesNotExist:
                word = Word(
                    cross_site_available=True,
                    cross_site_id=card_data['id'],
                    cross_site_site_name=site_name
                )
            word.word = card_data['question']
            word.word_string = card_data['question_pronunciation']
            word.packet = packet
            word.order = counter

            if card_data['additional_info'] is not None:
                for key, value in card_data['additional_info'].items():
                    if hasattr(word, key):
                        setattr(word, key, value)

            try:
                word.full_clean()
                word.save()
                result['words'].append(word.to_dict())
            except ValidationError as e:
                result['errors'].append(dict(
                    id=card_data['id'],
                    field_errors=e.message_dict,  # Include field-specific errors
                    message="Error validating word",
                    code=consts.CARD_WORD_VALIDATION_ERROR_CODE
                ))
                continue

            try:
                translation = WordTranslation.objects.get(
                    word=word
                )
            except WordTranslation.DoesNotExist:
                translation = WordTranslation(
                    word=word
                )
            translation.translation = card_data['answer']
            translation.translation_string = card_data['answer_pronunciation']

            try:
                translation.full_clean()
                translation.save()
                result['translations'].append(translation.to_dict())
            except ValidationError as e:
                result['errors'].append(dict(
                    id=card_data['id'],
                    field_errors=e.message_dict,  # Include field-specific errors
                    message="Error validating translation",
                    code=consts.CARD_TRANSLATION_VALIDATION_ERROR_CODE
                ))
                continue

            saved_words_ids.append(word.cd_id)
        words_for_deletion_ids = list(filter(lambda pk: pk not in saved_words_ids, packet_words_ids))
        for word_for_deletion_id in words_for_deletion_ids:
            try:
                word_for_deletion = Word.objects.get(cd_id=word_for_deletion_id)
                deletion_result = word_for_deletion.delete()
                result['deleted'].append(dict(
                    id=word_for_deletion.cross_site_id,
                    word=word_for_deletion.to_dict()
                ))
            except ProtectedError as e:
                result['notDeleted'].append(dict(
                    id=word_for_deletion.cross_site_id,
                    word=word_for_deletion.to_dict(),
                    reason=str(e),
                    reasonValue=len(e.protected_objects)
                ))
            except Word.DoesNotExist as e:
                continue

        result['success'] = True
        return JsonResponse(result, status=200)
    else:
        return HttpResponse('Only POST method allowed', status=405)


@csrf_exempt
def create_and_voice_word(request):
    try:
        data = json.loads(request.body)

        if data['key'] not in settings.DICTIONARY_CROSS_SITE_KEYS.keys():
            return JsonResponse({ 'success':False, 'message':'Wrong key'}, status=403)
        else:
            site_name = settings.DICTIONARY_CROSS_SITE_KEYS[data['key']]

        card_data = data['card']

        partner, partner_created = Partner.objects.get_or_create(
            name=data['partner']['name'],
        )

        packet, packet_created = Packet.objects.get_or_create(
            cross_site_id=data['table']['id'],
            cross_site_available=True,
            cross_site_site_name=site_name,
            partner=partner,
        )
        if packet_created and packet.name != data['table']['name']:
            packet.name = data['table']['name']
            packet.save()

        try:
            word = Word.objects.get(pk=data['card']['remoteId'])
        except Word.DoesNotExist:
            word = Word(
                packet=packet,
                cross_site_available=True,
                cross_site_id=card_data['id'],
                cross_site_site_name=site_name
            )

        word_voiceover_data_changed = False
        try:
            for json_name,field_name in WORD_JSON_FIELDS_TO_PYTHON.items():
                if getattr(word, field_name) != card_data.get(json_name, None):
                    word_voiceover_data_changed = True
                setattr(word, field_name, card_data.get(json_name, None))
        except KeyError as e:
            return JsonResponse({ 'success':False, 'message':f"Key Error in the card data: {str(e)}"}, status=400)

        validation_errors = []
        voiceover_errors = []
        try:
            word.full_clean()
            word.save()

            if word_voiceover_data_changed:
                try:
                    word.create_polly_task_v2()
                except BaseException as e:
                    message = str(e)
                    voiceover_errors.append({'word_string': [gettext_lazy('Error creating voiceover') + f': {message}'], 'word': [gettext_lazy('Error creating voiceover') + f': {message}']})

        except ValidationError as e:
            validation_errors.append(e.message_dict)

        if word.first_translation is not None:
            translation = word.first_translation
        else:
            translation = WordTranslation(
                word=word
            )

        translation_voiceover_data_changed = False
        for json_name, field_name in TRANSLATION_JSON_FIELDS_TO_PYTHON.items():
            if getattr(translation, field_name) != card_data.get(json_name, None):
                translation_voiceover_data_changed = True
            setattr(translation, field_name, card_data.get(json_name, None))
        try:
            translation.full_clean()
            translation.save()

            if translation_voiceover_data_changed:
                try:
                    translation.create_yandex_task()
                except:
                    voiceover_errors.append({'translation_string': [gettext_lazy('Error creating voiceover')], 'translation': [gettext_lazy('Error creating voiceover')]})

        except ValidationError as e:
            validation_errors.append(e.message_dict)

        return JsonResponse({
            'success':True,
            'word':word.to_dict(),
            'packet': packet.to_dict(),
            'saveErrors': validation_errors,
            'voiceoverErrors': voiceover_errors,
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'JSONDecodeError'}, status=400)
    except Word.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Word not found'}, status=404)


@csrf_exempt
def delete_cross_site_words(request, packet_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message':'Only POST method allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({'success': False, 'message':'JSONDecodeError'}, status=400)
    if data['key'] not in settings.DICTIONARY_CROSS_SITE_KEYS.keys():
        return JsonResponse({'success': False, 'message':'Wrong key'}, status=403)
    result = {
        'deleted':[],
        'notDeleted': [],
        'notFound': data['cardsIDs']
    }
    packet = Packet.objects.get(id=packet_id)
    words_to_delete = Word.objects.filter(packet=packet).exclude(cross_site_id__in=data['cardsIDsToStay'])
    for word in words_to_delete:
        try:
            deletion_result = word.delete()
            result['deleted'].append(dict(
                id=word.cross_site_id,
                word=word.to_dict(),
                deletionResult=deletion_result
            ))
            try:
                result['notFound'].remove(word.cross_site_id)
            except ValueError:
                pass
        except ProtectedError as e:
            if data['confirmed']:
                ...
            result['notDeleted'].append(dict(
                id=word.cross_site_id,
                word=word.to_dict(),
                reason=str(e),
                reasonValue=len(e.protected_objects)
            ))
            word.is_archived = True
            word.save(update_fields=['is_archived'])
    return JsonResponse(dict(success=True, **result))


class GetUserCrossSiteData(View):
    def get(self, request):
        data = request.json_data

        obj_type = data.get('type', None)
        if obj_type is None:
            return JsonResponse({'success': False, 'message': f'Missing parameter \'type\''})
        obj_ids = data.get('ids', [])

        if obj_type == 'packet':
            if data['ids']:
                packets = Packet.objects.filter(pk__in=obj_ids, cross_site_name=request.cross_site_name)
            else:
                packets = Packet.objects.filter(cross_site_name=request.cross_site_name)
            result = [packet.to_dict(request.user) for packet in packets]
        elif obj_type == 'words':
            words = Word.objects.filter(pk__in=obj_ids)
            result = [word.to_dict(user=request.user) for word in words]
        else:
            return JsonResponse({
                'success': False, 'message': f"No such data type: {obj_type}"
            }, status=400)

        return JsonResponse({
            'success': True, 'data': result
        }, status=200)

    def post(self, request):
        data = request.json_data
        action = data.get('action', None)
        if action is None:
            return JsonResponse({'success': False, 'message': f'Missing parameter: \'action\''})

        if action == 'store_user_packet':
            word_ids = data['ids']
            words_ids = Word.objects.filter(pk__in=word_ids, packet__cross_site_name=request.cross_site_name).values_list('cd_id', flat=True)
            UserStandalonePacket.objects.update(filters=None, words=words_ids)
            return JsonResponse({'success': True, 'data': words_ids})
        else:
            return JsonResponse({
                'success': False, 'message': f'No sauch action type: \'{action}\''
            }, status=400)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            request.json_data = json.loads(request.body)
        except (JSONDecodeError, ValueError):
            return JsonResponse(
                {'success': False, 'message': 'Invalid JSON'},
                status=400
            )
        except AttributeError:
            return JsonResponse(
                {'success': False, 'message': 'No JSON data provided'},
                status=400
            )

        key = request.json_data.get('key')
        if not key or key not in settings.DICTIONARY_CROSS_SITE_KEYS.keys():
            return JsonResponse({'success': False, 'message': 'Wrong key'}, status=403)
        request.cross_site_name = settings.DICTIONARY_CROSS_SITE_KEYS.get(key)
        user_id = request.json_data.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Missing user_id'}, status=400)
        try:
            request.user = User.objects.get(pk=request.json_data['user_id'])
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': f'User with id {request.json_data["user_id"]} does not exist'}, status=404)

        return super().dispatch(request, *args, **kwargs)


from rest_framework.views import APIView
from le_francais.permsissions import IsValidCourses

class UpdateUserStandalonePacketView(APIView):
    permission_classes = [IsValidCourses]

    def post(self, request):
        payload = getattr(request, 'service_payload', None)
        if not payload:
            return JsonResponse({'success': False, 'message': 'Invalid token payload'}, status=401)

        user_id = payload.get('user_id')
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

        try:
            data = request.data
            words_ids = data.get('words', [])
            if not isinstance(words_ids, list):
                return JsonResponse({'success': False, 'message': 'words must be a list'}, status=400)

            packet, created = UserStandalonePacket.objects.get_or_create(user=user)
            packet.words = [int(w) for w in words_ids]
            packet.save(update_fields=['words'])

            return JsonResponse({'success': True})

        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)


