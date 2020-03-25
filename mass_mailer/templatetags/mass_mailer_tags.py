from django.template.defaulttags import register


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
