from unidecode import unidecode

from conjugation.consts import LAYOUT_EN, LAYOUT_RU, VOWELS_LIST

import collections

def flatten(d, parent_key='', sep='_'):
	items = []
	for k, v in d.items():
		new_key = parent_key + sep + k if parent_key else k
		if isinstance(v, collections.MutableMapping):
			items.extend(flatten(v, new_key, sep=sep).items())
		else:
			items.append((new_key, v))
	return dict(items)


def index_tuple(l, value, index=0):
	"""
	Returns index of tuple in list of tuples, which [j] element is the same as s string
	:param index: index for searching tuples
	:param l: target list
	:param value: search string
	:return: index of tuple
	:rtype: int
	"""
	for pos, t in enumerate(l):
		if t[index] == value:
			return pos
	raise ValueError("list.index(x): x not in list")


def autocomplete_forms_startswith(s, reflexive=False, limit=50):
	"""
	Returns autocomplete list of verbs which forms starts with search string
	:param limit: limits the sql request
	:param reflexive: returns only reflexive verbs
	:param s: search string
	:return: autocomplete list of dictionaries with "url", "verb" and "html" keys
	"""
	autocomplete_list = []
	verbs = search_verbs_with_forms(s, limit)
	verbs.sort(key=lambda x: x[1][0][2] != 'infinitive-present')
	for verb, forms_list in verbs:
		cur_reflexive = False  # indicates that current verb must be reflexive
		if reflexive and verb.can_reflexive or verb.reflexive_only:
			verb = verb.reflexiveverb
			cur_reflexive = True
		elif reflexive and not (verb.can_reflexive or verb.reflexive_only):
			continue
		first_form = forms_list[0][0]
		is_infinitive = forms_list[0][2] == 'infinitive-present'
		if cur_reflexive and is_infinitive:
			if first_form[0] in VOWELS_LIST:
				r_html = f"s'<b>{first_form[:len(s)]}</b>{first_form[len(s):]}"
				first_form = f"s'{first_form}"
			else:
				r_html = f"se <b>{first_form[:len(s)]}</b>{first_form[len(s):]}"
				first_form = f"se {first_form}"
		if first_form != verb.infinitive:
			forms_html = ', '.join(
				[f'<b>{f[0][:len(s)]}</b>{f[0][len(s):]}' for f in forms_list])
			html = f'{verb.infinitive} ({forms_html})'
			url =  f'{verb.get_absolute_url()}#form{forms_list[0][4] or 0}'
		else:
			url = verb.get_absolute_url()
			if cur_reflexive:
				html = r_html
			else:
				html = f'<b>{verb.infinitive[:len(s)]}</b>{verb.infinitive[len(s):]}'
		autocomplete_list.append(dict(
			url=url,
			verb=verb.infinitive,
			html=html,
			isInfinitive=is_infinitive
		))
	return autocomplete_list


def autocomplete_infinitive_contains(s, reflexive=False, limit=50):
	"""

	:param s:
	:param reflexive:
	:param limit:
	:return:
	"""
	autocomplete_list = []
	from conjugation.models import Verb
	verbs = Verb.objects.filter(infinitive_no_accents__contains=s).exclude(infinitive_no_accents__startswith=s).order_by('-count')[:limit]
	for verb in verbs:
		if reflexive and verb.can_reflexive or verb.reflexive_only:
			verb = verb.reflexiveverb
		elif reflexive and not (verb.can_reflexive or verb.reflexive_only):
			continue
		pos_start = verb.infinitive_no_accents.find(s)
		pos_end = pos_start + len(s)
		html = f"{verb.infinitive[:pos_start]}<b>{verb.infinitive[pos_start:pos_end]}</b>{verb.infinitive[pos_end:]}"
		autocomplete_list.append(dict(
			url=verb.get_absolute_url(),
			verb=verb.infinitive,
			html=html,
			isInfinitive=True,
		))
	return autocomplete_list


def search_verbs(s, reflexive=None, return_first=False):
	s_unaccent = unidecode(s)
	verb = None
	verbs = []
	try:
		from conjugation.models import Verb
		verb = Verb.objects.get(infinitive_no_accents=s_unaccent)
		verbs.append((verb, None))
	except Verb.DoesNotExist:
		try:
			verbs_for_search = list(Verb.objects.raw(
				f"SELECT * FROM conjugation_verb "
				f"WHERE position(main_part_no_accents in '{s_unaccent}')=1 "
				f"ORDER BY CHAR_LENGTH (main_part) DESC"
			))
			for searching_verb in verbs_for_search:
				form = searching_verb.find_form(s)
				if form is not None:
					verb = searching_verb
					verbs.append((verb, form))
					if return_first:
						break
			if verb is None:
				raise Verb.DoesNotExist
		except Verb.DoesNotExist:
			if return_first:
				return None, None
			else:
				return [(None, None)]
	except Verb.MultipleObjectsReturned:
		try:
			verbs.append((Verb.objects.get(infinitive=s), None))
		except Verb.DoesNotExist:
			verbs.append((Verb.objects.filter(
				infinitive_no_accents=s_unaccent).first(), None))
			if not verbs:
				if return_first:
					return None, None
				else:
					return [(None, None)]
	for i, (v, f) in enumerate(verbs):
		if reflexive and (v.can_reflexive or v.reflexive_only):
			verbs[i] = v.reflexiveverb
	if return_first:
		return verbs[0]
	else:
		return verbs


def search_verbs_with_forms(s, limit=50, exact=False):
	"""
	Find and returns all verbs with forms starting with the search string
	:param limit: sql request limit
	:param s: utf decoded search string
	:type s: str
	:return: list of tuple (verb, forms)
		WHERE
		Verb verb is verb object
		list forms is list of tuples (form, mood, tense, person, n)
			WHERE
			str form is founded form of the verb;
			str mood is name of the mood;
			str tense is name of the tense;
			str person is name of the person;
			int n is number of form or None;
	:rtype: List[Verb, List[Tuple[str, str, str, str, int]]]
	"""
	verbs_list = []
	like_s = s + '%'
	from conjugation.models import Verb
	verbs_for_search = list(Verb.objects.raw(
		"SELECT * FROM conjugation_verb "
		"WHERE position(main_part_no_accents in %s)=1 "
		"OR main_part_no_accents LIKE %s "
		"ORDER BY count DESC, CHAR_LENGTH (main_part) DESC LIMIT %s", [s, like_s, limit+3]
	))
	for searching_verb in verbs_for_search:
		found_forms = searching_verb.find_forms(s, exact=exact)
		if found_forms:
			verbs_list.append((searching_verb, found_forms))
	return verbs_list[:limit]


def switch_keyboard_layout(s: str):
	for n in range(LAYOUT_EN.__len__()):
		s = s.replace(LAYOUT_RU[n], LAYOUT_EN[n])
	return s
