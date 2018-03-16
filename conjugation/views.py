from conjugation.models import Verb as V
from django.http import Http404, JsonResponse, HttpResponse
from .utils import get_conjugations

def get_conjugation(request, verb):
    try:
        v = V.objects.get(infinitive=verb)
    except V.DoesNotExist:
        raise Http404('Verb does not exist')
    return JsonResponse(get_conjugations(v))
