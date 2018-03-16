from conjugation.models import Verb
from django.http import Http404, JsonResponse

from .models import Verb


def get_conjugation(request, verb):
    try:
        v = Verb.objects.get(infinitive=verb)
    except Verb.DoesNotExist:
        raise Http404('Verb does not exist')
    d = dict(
        infinitive=v.template.infinitive,
        indicative=v.template.indicative,
        conditional=v.template.conditional,
        subjunctive=v.template.subjunctive,
        imperative=v.template.imperative,
        participle=v.template.participle,
    )
    return JsonResponse(d)
