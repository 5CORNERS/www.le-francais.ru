import re


def create_or_update_repetition(user_id, word_id, repetition_datetime, time):
	from .models import UserDayRepetition
	from .models import UserWordRepetition
	repetition, repetition_created = UserWordRepetition.objects.get_or_create(
		user_id=user_id,
		word_id=word_id,
	)
	repetition.repetition_datetime = repetition_datetime
	repetition.time = time
	repetition.save()
	if not repetition_created:
		for old_day_repetitions in UserDayRepetition.objects.filter(
				repetitions__contains=[repetition.pk]):
			old_day_repetitions.repetitions.remove(repetition.pk)
			old_day_repetitions.save()
	if repetition.time < 5:
		day_repetitions, day_repetition_created = UserDayRepetition.objects.get_or_create(
			user_id=user_id,
			datetime=repetition_datetime
		)
		if day_repetition_created:
			day_repetitions.repetitions = []
		if (day_repetitions.repetitions is None or
				not repetition.pk in day_repetitions.repetitions):
			day_repetitions.repetitions.append(repetition.pk)
		if not day_repetition_created:
			# deleting existing repetition from old day_repetition
			# needs reworking
			to_remove = list(UserWordRepetition.objects.filter(
				pk__in=day_repetitions.repetitions
			).exclude(
				repetition_datetime__exact=repetition_datetime
			).exclude(
				pk=repetition.pk
			).distinct().values_list('pk', flat=True))
			if to_remove:
				day_repetitions.repetitions = [
					x for x in day_repetitions.repetitions if
					x not in to_remove
				]
		day_repetitions.save()
	return repetition



def message(n, form1='новое слово', form2='новых слова', form5='новых слов'):
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return '{0} {1}'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return '{0} {1}'.format(str(n), form2)
    else:
        return '{0} {1}'.format(str(n), form5)


def format_text2speech(text):
	# FIXME ignore double parentheses
	text = remove_parenthesis(text)
	text = text.replace(';', '.')
	text = '. '.join([s[0].capitalize() + s[1:] for s in text.split('. ')])
	return text


def remove_parenthesis(text):
	text = ''.join([s.split(')')[-1] for s in
					text.split('(')])  # ignore parentheses
	text = re.sub(' +', ' ', text)  # remove multiple whitespaces
	return text


def clean_filename(filename:str):
	return remove_parenthesis(filename.strip(' ')\
		.strip(' ')\
		.replace('\'', '_') \
	  	.replace(' ', '_') \
		.replace('\\', '_').replace('/', '_')\
		.replace(' ', '_')\
		.replace('*', ''))\
		.replace('?', '_')\
		.replace('__', '_')\
		.replace(' ', '_')
# helper.bulk_update(to_update, update_fields=['_polly_url'])


import os
from shutil import copyfile
def copy_file(src, dest):
	if os.path.exists(dest):
		return True
	elif not os.path.exists(src):
		return False
	else:
		copyfile(src, dest.lower())
		return True


def escape_non_url_characters(str):
	return str.replace(' ', '_').replace('\\', '_').replace('/', '_')


_courses_public_key = None


def load_courses_public_key():
    global _courses_public_key
    if _courses_public_key is None:
        import os
        from django.conf import settings
        key_path = os.path.join(settings.BASE_DIR, 'courses_public.pem')
        if not os.path.exists(key_path):
            key_path = 'courses_public.pem'
        with open(key_path, 'r') as key_file:
            _courses_public_key = key_file.read()
    return _courses_public_key


def login_from_courses_token(request):
    token = request.GET.get('token')
    if not hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    if not token:
        return None
    import sys
    import jwt
    from django.contrib.auth import login
    from custom_user.models import User
    try:
        views_mod = sys.modules.get('le_francais_dictionary.views')
        if views_mod and hasattr(views_mod, 'load_courses_public_key'):
            public_key = views_mod.load_courses_public_key()
        else:
            public_key = load_courses_public_key()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            issuer='courses.le-francais.ru',
            audience='www.le-francais.ru'
        )
        user_id = payload.get('user_id')
        if not user_id:
            return None
        user = User.objects.get(pk=user_id, is_active=True)
        if request.user.is_authenticated and request.user.pk == user.pk:
            return user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.user = user
        if hasattr(request, 'session'):
            request.session.save()
        return user
    except Exception:
        return None
