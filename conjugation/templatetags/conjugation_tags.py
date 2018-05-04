from django import template
from django.urls import reverse
from home.models import PageLayoutAdvertisementSnippet

register = template.Library()

@register.assignment_tag(takes_context=True)
def option_url(context, option):
    feminin = context.dicts[3]['feminin']
    reflexive = context.dicts[3]['reflexive']

    if option == 'gender':
        feminin = not feminin
    elif option == 'se':
        reflexive = not reflexive

    if feminin:
        gender = 'feminin_'
    else:
        gender = ''

    if reflexive:
        pronominal = 'se_'
    else:
        pronominal = ''

    return reverse('conjugation:verb',kwargs=dict(feminin=gender, se=pronominal, verb=context.dicts[3]['v'].infinitive_no_accents))

@register.inclusion_tag('tags/conjugation_advert_body.html')
def conjugation_advertisement_body(code):
    try:
        return dict(body=PageLayoutAdvertisementSnippet.objects.filter(code=code).exclude(live=False)[0].body)
    except:
        return dict(body=None)

@register.inclusion_tag('tags/conjugation_advert_head.html')
def conjugation_advertisement_head(code):
    try:
        return dict(head=PageLayoutAdvertisementSnippet.objects.filter(code=code).exclude(live=False)[0].head)
    except:
        return dict(head=None)