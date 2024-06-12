from django.template.defaulttags import register
from ..models import Profile


@register.simple_tag(takes_context=False)
def message(val, form1, form2, form5):
	n10 = val % 10
	n100 = val % 100
	if n10 == 1 and n100 != 11:
		return f'{val} {form1}'
	elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
		return f'{val} {form2}'
	else:
		return f'{val} {form5}'

@register.filter(takes_context=False)
def n_to_word(s:str):
	if "5 " in s:
		s = s.replace("5 ", "пять ")
	elif "1 " in s:
		s = s.replace("1 ", "")
	return s

@register.assignment_tag(takes_context=False)
def get_mass_mailer_profile_by_user(user):
	return Profile.objects.get(user=user)