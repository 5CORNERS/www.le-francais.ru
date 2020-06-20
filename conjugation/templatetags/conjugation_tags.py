from django import template

from conjugation.utils import get_url_from_switches
from home.models import PageLayoutAdvertisementSnippet

register = template.Library()

@register.assignment_tag(takes_context=True)
def option_url(context, option):
    feminin = context.dicts[3]['feminin']
    reflexive = context.dicts[3]['reflexive']
    passive = context.dicts[3]['passive']
    negative = context.dicts[3]['negative']
    question = context.dicts[3]['question']

    if option == 'gender':
        feminin = not feminin
    elif option == 'reflexive':
        reflexive = not reflexive
    elif option == 'passive':
        passive = not passive
    elif option == 'negative':
        negative = not negative
    elif option == 'question':
        question = not question

    infinitive = context.dicts[3]['v'].infinitive_no_accents

    return get_url_from_switches(infinitive, negative, question, passive, reflexive, feminin)


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
