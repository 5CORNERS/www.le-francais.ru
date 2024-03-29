from dal import autocomplete
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, \
	HttpResponsePermanentRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from unidecode import unidecode

from conjugation import forms
from conjugation.models import Verb, PollyAudio, Translation, \
	FrTag, RuTag
from polly.models import PollyTask
from .consts import *
from .forms import SwitchesForm
from polly.const import *
from .table import Table, Tense
from .utils import search_verbs, switch_keyboard_layout, \
	search_verbs_with_forms, autocomplete_verb, get_url_from_switches


@require_http_methods(["POST"])
def get_polly_audio_link(request):
	key = request.POST.get('key')
	task_completed = False
	polly_audio, created = PollyAudio.objects.select_related('polly').get_or_create(key=key)
	text = Tense(key=key).get_polly_ssml()
	# if polly_audio.polly and polly_audio.polly.text != text:
	# 	polly_audio.delete()
	# 	polly_audio, created = PollyAudio.objects.select_related('polly').get_or_create(key=key)
	if created or polly_audio.polly is None or polly_audio.polly.url is None:
		polly_task = PollyTask(
			text=text,
			text_type=TEXT_TYPE_SSML,
			language_code=LANGUAGE_CODE_FR,
			sample_rate=SAMPLE_RATE_22050,
			voice_id=VOICE_ID_LEA,
			output_format=OUTPUT_FORMAT_MP3,
			datetime_creation=timezone.now()
		)
		polly_task.create_task('polly-conjugations/', wait=False, save=True)
		polly_audio.polly = polly_task
		polly_audio.save()
	elif polly_audio.polly.task_status != 'completed':
		polly_audio.polly.update_task()
		if polly_audio.polly.task_status == 'completed':
			task_completed = True
	else:
		task_completed = True
	if task_completed:
		return JsonResponse(data={key: {'url': polly_audio.polly.url}})
	else:
		return JsonResponse(data={
			key: {'url': reverse(
				'conjugation:polly_listen', kwargs={'pk':polly_audio.pk}
			)}
		})

def get_polly_audio_stream(request, pk):
	polly_audio = PollyAudio.objects.get(pk=pk)
	stream = polly_audio.polly.get_audio_stream()
	response = HttpResponse(stream.read(), content_type='audio/mp3')
	stream.close()
	return response

@csrf_exempt
def search(request):
	if request.method == 'post':
		search_string = switch_keyboard_layout(str(request.POST.get('q')).strip(' ').lower())
	else:
		search_string = switch_keyboard_layout(str(request.GET.get('q')).strip(' ').lower())
	search_string = search_string.replace('’', '\'')
	is_reflexive = False
	is_pronoun = False
	if search_string.find("s'en ") == 0:
		search_string = search_string[5:]
		is_pronoun = True
	elif search_string.find("s'") == 0:
		search_string = search_string[2:]
		is_reflexive = True
	elif search_string.find("se ") == 0:
		search_string = search_string[3:]
		is_reflexive = True
	found_forms = []
	for verb, forms in search_verbs_with_forms(search_string, exact=True):
		if verb.infinitive == search_string:
			found_forms.append(dict(
				url=verb.get_absolute_url(),
				infinitive=verb.infinitive,
				conjugation=search_string,
				mood='Infinitif',
				tense='présent',
				person='—'
			))
			break
		for form in forms:
			gender = GENDER_MASCULINE
			person_index = form[3]
			if form[2] == 'past-participle':
				if person_index in [2, 3]:
					person_index -= 2
					gender = GENDER_FEMININE
			# FIXME fix Table arguments
			conjugation = Table(
				v=verb,
				gender=gender,
				reflexive=is_reflexive,
				pronoun=is_pronoun,
			).get_conjugation(
				form[1], form[2], person_index, form[4] or 0)
			if form[2] in PERSONS.keys():
				persons_keys = PERSONS[form[2]]
			else:
				persons_keys = PERSONS['other']
			if conjugation:
				found_forms.append(dict(
					url=verb.get_absolute_url(),
					infinitive=verb.infinitive,
					conjugation=conjugation,
					mood=next((mood[1] for mood in MOODS if form[1] == mood[0]), ''),
					tense=next((tense[1] for tense in TENSES if form[2] == tense[0]), ''),
					person=next((person[1] for person in persons_keys if form[3] == person[0]), '')
				))
	if len(found_forms) > 1:
		return render(request, 'conjugation/verb_found_forms.html',
		              {'search_string': search_string, 'found_forms': found_forms})
	verb, form = search_verbs(search_string, is_reflexive, return_first=True, is_pronoun=is_pronoun)
	if verb is None:
		autocomplete_list = autocomplete_verb(search_string, is_reflexive, 50, is_pronoun=is_pronoun)
		return render(request, 'conjugation/verb_not_found.html',
		              {'search_string': search_string, 'autocomplete_list': autocomplete_list})
	if is_pronoun:
		url = verb.get_url(pronoun=True, voice=VOICE_REFLEXIVE)
	else:
		url = verb.get_absolute_url()
	return redirect(url)


@csrf_exempt
def verb_switches_form_view(request):
	if request.method == 'POST':
		form = SwitchesForm(request.POST)
		if form.is_valid():
			data:dict = form.cleaned_data
		else:
			return HttpResponseBadRequest()
		lock = data.pop('lock', False)
		url = get_url_from_switches(
			**data
		)
		return HttpResponseRedirect(url)
	else:
		return HttpResponseBadRequest()


def index(request):
	return render(request, 'conjugation/index.html', dict(frequent_urls=FREQUENT_URLS))


def verb_page_redirect(request, feminin, question, negative, passive, reflexive, pronoun, verb, homonym):
	return HttpResponsePermanentRedirect(reverse('conjugation:verb', kwargs=dict(
		feminin='_feminin' if bool(feminin) else '',
		question='_question' if bool(question) else '',
		negative='_negation' if bool(negative) else '',
		passive='_voix-passive' if bool(passive) else '',
		reflexive=reflexive or '',
		pronoun=pronoun or '',
		verb=verb,
		homonym=homonym or ''
	)))


# FIXME: s'appler feminine form
def verb_page(request, feminin, question, negative, passive, reflexive, pronoun, verb, homonym):
	url_kwargs = dict(
		feminin=feminin or '', question=question or '', negative=negative or '', passive=passive or '',
		reflexive=reflexive or '',
		pronoun=pronoun or '', verb=verb, homonym=homonym or ''
	)
	word_no_accent = unidecode(verb)
	try:
		verb = Verb.objects.get(infinitive_no_accents=word_no_accent)
	except Verb.DoesNotExist:
		return render(request, 'conjugation/verb_not_found.html',
					  {'search_string': word_no_accent})
	except Verb.MultipleObjectsReturned:
			try:
				if homonym:
					verb = Verb.objects.get(infinitive_no_accents=word_no_accent, homonym=2)
				else:
					verb = Verb.objects.get(infinitive_no_accents=word_no_accent, homonym=1)
			except Verb.DoesNotExist:
				verb = Verb.objects.filter(infinitive_no_accents=word_no_accent).first()
	if request.POST:
		switches_form = SwitchesForm(request.POST)
		if switches_form.is_valid():
			data = switches_form.cleaned_data
			lock = data.pop('lock', False)
			url = verb.get_url(
				negative=data['negative'],
				question=data['question'],
				voice=VOICE_PASSIVE if data['passive'] else VOICE_REFLEXIVE if data['reflexive'] else VOICE_ACTIVE,
				pronoun=data['pronoun'],
				gender=GENDER_FEMININE if data['feminine'] else GENDER_MASCULINE
			)
			return HttpResponseRedirect(url)
		else:
			return HttpResponseBadRequest()
	else:
		badges = []

		needs_redirect = False
		if verb.reflexive_only and not (reflexive or pronoun):
			url_kwargs['reflexive'] = 's_' if verb.reflexiveverb.is_short() else 'se_'
			needs_redirect = True

		elif reflexive and not pronoun and not verb.can_reflexive and not verb.reflexive_only:
			url_kwargs['reflexive'] = ''
			needs_redirect = True

		elif not (verb.reflexive_only or verb.can_reflexive or verb.can_be_pronoun) and reflexive:
			url_kwargs['reflexive'] = ''
			needs_redirect = True

		elif (reflexive == "se_" and verb.reflexiveverb.is_short()) or (reflexive == "s_" and not verb.reflexiveverb.is_short()):
			url_kwargs['reflexive'] = 's_' if verb.reflexiveverb.is_short() else 'se_'
			needs_redirect = True

		if not verb.can_passive and passive:
			url_kwargs['passive'] = ''
			needs_redirect = True

		if not verb.can_be_pronoun and pronoun:
			url_kwargs['pronoun'] = ''
			needs_redirect = True

		if needs_redirect:
			return redirect(reverse('conjugation:verb', kwargs=url_kwargs))

		reflexive = True if (verb.can_reflexive or verb.reflexive_only) and reflexive else False

		if negative:
			badges.append('отрицание')
		else:
			badges.append('утверждение')
		if question:
			badges.append('вопрос')
		else:
			badges.append('повествование')
		if reflexive or pronoun:
			badges.append("возвратный залог" + (f' (s\'en {verb.infinitive})' if pronoun else ''))
		elif passive:
			badges.append('пассивный залог')
		else:
			badges.append('активный залог')
		if feminin:
			feminin = True
			gender = GENDER_FEMININE
			badges.append('женский род')
		else:
			feminin = False
			gender = GENDER_MASCULINE
			badges.append('мужской род')

		verb.count += 1
		verb.save()
		verb.construct_conjugations()
		table = Table(
			v=verb,
			reflexive=reflexive,
			gender=gender,
			question=bool(question),
			passive=bool(passive),
			negative=bool(negative),
			pronoun=bool(pronoun),
			request=request
		)
		session = request.session
		was_on_conjugations = session.get('was_on_conjugations', False)
		if not was_on_conjugations:
			session['was_on_conjugations'] = True
		return render(request, 'conjugation/table.html', {
			'v': verb,
			'reflexive': bool(reflexive),
			'can_be_reflexive': verb.can_reflexive or verb.can_be_pronoun,
			'reflexive_only': verb.reflexive_only,
			'must_be_pronoun': not verb.can_reflexive and verb.can_be_pronoun,
			'feminin': feminin,
			'table': table,
			'forms_count': verb.template.forms_count,
			'forms_range': list(range(1, verb.template.forms_count + 1)),
			'question':bool(question),
			'passive':bool(passive),
			'negative':bool(negative),
			'pronoun':bool(pronoun),
			'switches_form': SwitchesForm(initial={
				'infinitive': verb.infinitive_no_accents,
				'negative': bool(negative),
				'question': bool(question),
				'feminine': bool(feminin),
				# 0 — ACTIVE
				# 1 — PASSIVE
				# 2 — REFLEXIVE
				'voice': 1 if passive else 2 if reflexive or pronoun else 0,
				'pronoun': pronoun,
			}),
			'badges': badges,
		})


def get_autocomplete_list(request):
	list_len = 50
	_term = request.GET['term'].lower()
	term = switch_keyboard_layout(_term[:255] if len(_term) > 255 else _term).replace('’', '\'')
	term = unidecode(term)
	reflexive = False
	pronoun = False
	s = term
	if term[:5] == 's\'en ':
		pronoun = True
		s = term[5:]
	elif term[:3] == 'se ' or term[:2] == "s'":
		reflexive = True
		s = term[3:] if term.startswith('se ') else term[2:]
	autocomplete_list = autocomplete_verb(s, reflexive, list_len, is_pronoun=pronoun)
	return JsonResponse(autocomplete_list[:list_len], safe=False)


class TranslationUpdateView(View):
	"""For adding translations and phrasems to a verb and editing them."""

	def get(self, request, pk):
		verb = Verb.objects.get(id=pk)
		main_formset = modelformset_factory(
			Translation, form=forms.VerbMainForm,
			extra=0,
		)
		examples_formset = modelformset_factory(
			Translation,
			form=forms.VerbExampleForm,
			extra=0,
		)
		collocations_formset = modelformset_factory(
			Translation,
			form=forms.VerbCollocationForm,
			extra=0,
		)
		idioms_formset = modelformset_factory(
			Translation,
			form=forms.VerbIdiomForm,
			extra=0,
		)
		return render(
			request,
			'conjugation/verb_translation_update.html',
			{
				'formsets': [
					('main', main_formset(initial=[{'fr_verb': verb, 'order': 0}],
					                      prefix='main')),
					('examples', examples_formset(
						initial=[{'fr_verb': verb, 'order': 0}],
						prefix='examples')),
					('collocations', collocations_formset(
						initial=[{'fr_verb': verb, 'order': 0}],
						prefix='collocations')),
					('idioms', idioms_formset(
						initial=[{'fr_verb': verb, 'order': 0}], prefix='idioms'))
				],
				'verb': verb
			}
		)


class FrVerbAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return Verb.objects.none()

		qs = Verb.objects.all()

		if self.q:
			qs = qs.filter(infinitive_no_accents__istartswith=self.q)

		return qs


class FrTagAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return FrTag.objects.none()
		qs = FrTag.objects.all()

		if self.q:
			qs = qs.filter(tag__istartswith=self.q)

		return qs


class TranslationTagAutocomplete(autocomplete.Select2QuerySetView):

	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return RuTag.objects.none()

		qs = RuTag.objects.all()

		if self.q:
			qs = qs.filter(tag__istartswith=self.q)

		return qs
