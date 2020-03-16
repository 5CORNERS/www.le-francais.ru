from dal import autocomplete
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from unidecode import unidecode

from conjugation import forms
from conjugation.models import Verb, ReflexiveVerb, PollyAudio, Translation, \
	FrTag, RuTag
from polly.models import PollyTask
from .consts import *
from .polly import *
from .table import Table, Tense
from .utils import autocomplete_forms_startswith, \
	autocomplete_infinitive_contains, search_verbs, switch_keyboard_layout, \
	search_verbs_with_forms


@require_http_methods(["POST"])
def get_polly_audio_link(request):
	key = request.POST.get('key')
	polly_audio, created = PollyAudio.objects.select_related('polly').get_or_create(key=key)
	if created or polly_audio.polly is None or polly_audio.polly.url is None:
		tense = Tense(key=key)
		polly_task = PollyTask(
			text=tense.get_polly_ssml(),
			text_type=TEXT_TYPE_SSML,
			language_code=LANGUAGE_CODE_FR,
			sample_rate=SAMPLE_RATE_22050,
			voice_id=VOICE_ID_LEA,
			output_format=OUTPUT_FORMAT_MP3,
		)
		polly_task.create_task('polly-conjugations/', wait=True, save=True)
		polly_audio.polly = polly_task
		polly_audio.save()
	return JsonResponse(data={key: {'url': polly_audio.polly.url}})


@csrf_exempt
def search(request):
	if request.method == 'post':
		search_string = switch_keyboard_layout(str(request.POST.get('q')).strip(' ').lower())
	else:
		search_string = switch_keyboard_layout(str(request.GET.get('q')).strip(' ').lower())
	reflexive = True
	if search_string.find("s'") == 0:
		search_string = search_string[2:]
	elif search_string.find("se ") == 0:
		search_string = search_string[3:]
	else:
		reflexive = False
	found_forms = []
	for verb, forms in  search_verbs_with_forms(search_string, exact=True):
		for form in forms:
			conjugation = Table(
				verb, 0, reflexive).get_conjugation(
				form[1], form[2], form[3], form[4] or 0)
			found_forms.append(dict(
				url=verb.get_absolute_url(),
				infinitive=verb.infinitive,
				conjugation=conjugation,
				mood=next((mood[1] for mood in MOODS if form[1] == mood[0]), ''),
				tense=next((tense[1] for tense in TENSES if form[2] == tense[0]), ''),
				person=next((person[1] for person in PERSONS if form[3] == person[0]), '')
			))
	if len(found_forms) > 1:
		return render(request, 'conjugation/verb_found_forms.html',
		              {'search_string': search_string, 'found_forms': found_forms})
	verb, form = search_verbs(search_string, reflexive, return_first=True)
	if verb is None:
		autocomplete_list = autocomplete_forms_startswith(search_string, reflexive)
		if len(autocomplete_list) < 50:
			autocomplete_list += autocomplete_infinitive_contains(search_string, reflexive,
			                                                      limit=50 - len(
				                                                      autocomplete_list))
		return render(request, 'conjugation/verb_not_found.html',
		              {'search_string': search_string, 'autocomplete_list': autocomplete_list})
	return redirect(verb.get_absolute_url())


def index(request):
	return render(request, 'conjugation/index.html', dict(frequent_urls=FREQUENT_URLS))


def verb_page(request, se, feminin, verb, homonym):
	word_no_accent = unidecode(verb)
	try:
		verb = Verb.objects.get(infinitive_no_accents=word_no_accent)
	except Verb.DoesNotExist:
		return render(request, 'conjugation/verb_not_found.html',
		              {'search_string': word_no_accent})
	except Verb.MultipleObjectsReturned:
		try:
			verb = Verb.objects.get(infinitive=verb)
		except:
			verb = Verb.objects.filter(infinitive_no_accents=word_no_accent).first()

	if feminin:
		feminin = True
		gender = -1
	else:
		feminin = False
		gender = 0

	if verb.reflexive_only and not se:
		return redirect(verb.reflexiveverb.get_absolute_url())
	if not (verb.reflexive_only or verb.can_reflexive) and se:
		return redirect(verb.get_absolute_url())

	if (se == "se_" and verb.reflexiveverb.is_short()) or (se == "s_" and not verb.reflexiveverb.is_short()):
		return redirect(verb.reflexiveverb.get_absolute_url())

	reflexive = True if (verb.can_reflexive or verb.reflexive_only) and se else False

	verb.count += 1
	verb.save()
	verb.construct_conjugations()
	table = Table(verb, gender, reflexive)
	return render(request, 'conjugation/table.html', {
		'v': verb,
		'reflexive': reflexive,
		'feminin': feminin,
		'table': table,
		'forms_count': verb.template.forms_count,
		'forms_range': list(range(1, verb.template.forms_count + 1))
	})


def get_autocomplete_list(request):
	list_len = 50
	_term = request.GET['term'].lower()
	term = switch_keyboard_layout(_term)
	term = unidecode(term)
	reflexive = False
	s = term
	if term[:3] == 'se ' or term[:2] == "s'":
		reflexive = True
		s = term[3:] if term.startswith('se ') else term[2:]
	autocomplete_list = autocomplete_forms_startswith(s, reflexive)
	if len(autocomplete_list) < list_len:
		autocomplete_list += autocomplete_infinitive_contains(s, reflexive, limit=list_len - len(autocomplete_list))
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
