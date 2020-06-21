from django.urls import reverse
from unidecode import unidecode

from conjugation.consts import LAYOUT_EN, LAYOUT_RU, VOWELS_LIST, GENDER_FEMININE, GENDER_MASCULINE

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


def autocomplete_forms_startswith(s, reflexive=False, limit=50,
                                  show_infinitives=10, show_forms=5):
	"""
	Returns autocomplete list of verbs which forms starts with search string
	:param show_infinitives: max index of infinitives item, after which others will be hidden
	:param show_forms: max index of forms item, after which others will be hidden
	:param limit: limits the sql request
	:param reflexive: returns only reflexive verbs
	:param s: search string
	:return: autocomplete list of dictionaries with "url", "verb" and "html" keys
	"""
	autocomplete_list_infinitives = []
	autocomplete_list_forms = []
	verbs = search_verbs_with_forms(s, limit)
	# verbs.sort(key=lambda x: x[1][0][2] != 'infinitive-present')
	infinitives_len = 0
	forms_len = 0
	for verb, forms_list in verbs:
		infinitive_contains_search_string = forms_list[0][2] == 'infinitive-present'
		current_is_reflexive = False
		infinitive = verb.infinitive
		if reflexive and verb.can_reflexive or verb.reflexive_only:
			verb = verb.reflexiveverb
			current_is_reflexive = True
		elif reflexive and not (verb.can_reflexive or verb.reflexive_only):
			continue # if user type s' or se skip non reflexive verbs
		cls = 'starts-with'
		if not infinitive_contains_search_string:
			cls = cls + '-form'
			forms_len += 1
			if forms_len > show_forms:
				cls = cls + ' load-more hide'
			forms = list(dict.fromkeys([a[0] for a in forms_list])) # removing duplicate forms
			forms_html = ', '.join(
				[f'<b>{f[:len(s)]}</b>{f[len(s):]}' for f in forms]
			) # comma-separated forms list
			html = f'{infinitive} <span style="font-size: 1.2em;">→</span> {forms_html}'
			url = f'{verb.get_absolute_url()}#form{forms_list[0][4] or 0}'
		else:
			cls = cls + '-infinitive'
			infinitives_len +=1
			if infinitives_len > show_infinitives:
				cls = cls + ' load-more hide'
			url = verb.get_absolute_url()
			html = f"<b>{infinitive[:len(s)]}</b>{infinitive[len(s):]}"
		if current_is_reflexive:
			if infinitive[0] in VOWELS_LIST:
				html = "s'" + html
			else:
				html = 'se ' + html
		item = dict(
			url=url,
			verb=verb.infinitive,
			html=html,
			isInfinitive=infinitive_contains_search_string,
			cls=cls,
		)
		if infinitive_contains_search_string:
			autocomplete_list_infinitives.append(item)
		else:
			autocomplete_list_forms.append(item)
	if autocomplete_list_infinitives:
		autocomplete_list_infinitives[-1]['cls'] = autocomplete_list_infinitives[-1][
		                               'cls'] + ' last-of-type'
	if autocomplete_list_forms:
		autocomplete_list_forms[-1]['cls'] = autocomplete_list_forms[-1][
		                               'cls'] + ' last-of-type'

	autocomplete_list = autocomplete_list_infinitives + autocomplete_list_forms
	return autocomplete_list


def autocomplete_infinitive_contains(s, reflexive=False, limit=50, max_show=5):
	"""

	:param max_show:
	:param s:
	:param reflexive:
	:param limit:
	:return:
	"""
	autocomplete_list = []
	from conjugation.models import Verb
	verbs = Verb.objects.filter(infinitive_no_accents__contains=s).exclude(
		infinitive_no_accents__startswith=s).order_by('-count')[:limit]
	count = 0
	for i, verb in enumerate(verbs):
		cls = 'contains'
		if reflexive and verb.can_reflexive or verb.reflexive_only:
			verb = verb.reflexiveverb
		elif reflexive and not (verb.can_reflexive or verb.reflexive_only):
			continue
		count += 1
		if count > max_show:
			cls += ' load-more hide'
		pos_start = verb.infinitive_no_accents.find(s)
		pos_end = pos_start + len(s)
		html = f"{verb.infinitive[:pos_start]}<b>{verb.infinitive[pos_start:pos_end]}</b>{verb.infinitive[pos_end:]}"
		autocomplete_list.append(dict(
			url=verb.get_absolute_url(),
			verb=verb.infinitive,
			html=html,
			isInfinitive=True,
			cls=cls,
		))
	if autocomplete_list:
		autocomplete_list[-1]['cls'] = autocomplete_list[-1][
		                               'cls'] + ' last-of-type'

	return autocomplete_list


def search_verbs(s, reflexive=None, return_first=False):
	from conjugation.models import Verb
	s_unaccent = unidecode(s)
	verb = None
	verbs = []
	try:
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
			verbs[i] = (v.reflexiveverb, f)
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
		"ORDER BY count DESC, CHAR_LENGTH (main_part) DESC LIMIT %s",
		[s, like_s, limit + 3]
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


def message(val, param1, param2, param5):
	n10 = val % 10
	n100 = val % 100
	if n10 == 1 and n100 != 11:
		return f'{val} {param1}'
	elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
		return f'{val} {param2}'
	else:
		return f'{val} {param5}'


def autocomplete_infinitive_levenshtein(s, reflexive, limit, max_distance=3,
                                        max_show=5):
	from .models import Verb
	autocomplete_list = []
	verbs = Verb.objects.raw('''SELECT * FROM
	(SELECT levenshtein_less_equal(%s, v.infinitive_no_accents,1,1,1, 12) as levenshtein, v.*
	FROM conjugation_verb v
	ORDER BY v.count DESC, levenshtein) t
	WHERE t.levenshtein <> 0 and t.levenshtein < %s LIMIT %s''',
	                         [s, max_distance, limit])

	count = 0
	for verb in verbs:
		levenshtein = verb.levenshtein
		cls = 'levenshtein'
		if reflexive and verb.can_reflexive or verb.reflexive_only:
			verb = verb.reflexiveverb
		elif reflexive and not (verb.can_reflexive or verb.reflexive_only):
			continue
		count += 1
		if count > max_show:
			cls += ' load-more hide'
		html = f'{verb.infinitive} ? <span class="levenshtein-typos">{message(levenshtein, "опечатка","опечатки","опечаток")}</span>'
		autocomplete_list.append(dict(
			url=verb.get_absolute_url(),
			verb=verb.infinitive,
			html=html,
			isInfinitive=True,
			cls=cls,
		))
	if autocomplete_list:
		autocomplete_list[-1]['cls'] = autocomplete_list[-1]['cls'] + ' last-of-type'
	return autocomplete_list


def autocomplete_verb(
		search_string, is_reflexive, limit, show_startswith_infinitive=99,
		show_startswith_forms=99, show_starts_with_levenshtein=5,
		show_startswith_contains=5):
	autocomplete_list_startswith = autocomplete_forms_startswith(
		search_string,
		is_reflexive,
		show_infinitives=show_startswith_infinitive,
		show_forms=show_startswith_forms)
	current_len = len(autocomplete_list_startswith)

	autocomplete_list_levenshtein = []
	if current_len < limit:
		autocomplete_list_levenshtein = autocomplete_infinitive_levenshtein(
			search_string,
             is_reflexive,
             limit=limit - current_len,
             max_distance=3 if current_len else 4,
             max_show=show_starts_with_levenshtein)
		current_len = current_len + len(autocomplete_list_levenshtein)

	autocomplete_list_contains = []
	if current_len < limit:
		autocomplete_list_contains = autocomplete_infinitive_contains(
			search_string,
			is_reflexive,
			limit=limit - current_len,
			max_show=show_startswith_contains
		)

	autocomplete_list = autocomplete_list_startswith + autocomplete_list_contains + autocomplete_list_levenshtein
	autocomplete_list = remove_autocomplete_duplicates(autocomplete_list)
	return autocomplete_list


def remove_autocomplete_duplicates(autocomplete_list):
	return [item for i, item in enumerate(autocomplete_list)
	        if not any(_item['url'].split('#')[0] == item['url'] for _item in autocomplete_list[:i])]


def get_url_from_switches(infinitive, negative, question, passive, reflexive, feminin):
    if feminin:
        gender = 'feminin_'
    else:
        gender = ''
    if reflexive:
        reflexive = 'se_'
    else:
        reflexive = ''
    if negative:
        negative = 'negation_'
    else:
        negative = ''
    if passive:
        passive = 'voix-passive_'
    else:
        passive = ''
    if question:
        question = 'question_'
    else:
        question = ''
    return reverse('conjugation:verb', kwargs=dict(
        feminin=gender,
        reflexive=reflexive,
        negative=negative,
        passive=passive,
        question=question,
        verb=infinitive
    ))


def switches_to_verb_url(switches, infinitive):
	gender, reflexive, question, negative, passive = parse_switches(switches)
	return reverse('conjugation:verb', kwargs={
		'feminin': 'feminin_' if gender == GENDER_FEMININE else '',
		'question': 'question_' if question else '',
		'negative': 'negation_' if negative else '',
		'passive': 'voix-passive_' if passive else '',
		'reflexive': 'se_' if reflexive else '',
		'verb': infinitive})


def parse_switches(s):
	gender = GENDER_MASCULINE
	reflexive = False
	negative = False
	question = False
	passive = False
	if 'feminine' in s and s['feminine']:
		gender = GENDER_FEMININE
	if "reflexive" in s and s['reflexive']:
		reflexive = True
	if "negative" in s and s['negative']:
		negative = True
	if 'question' in s and s['question']:
		question = True
	if 'passive' in s and s['passive']:
		passive = True
	return gender, reflexive, question, negative, passive
