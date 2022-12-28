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


@register.inclusion_tag('tags/conjugation_advert_body.html', takes_context=True)
def conjugation_advertisement_body(context, code):
    try:
        request = context.get('request')
        user = request.user
        if user.is_authenticated and user.has_payed and not code=='conjugations_sidebar_top':
            return dict(body=None)
        snippet:PageLayoutAdvertisementSnippet = PageLayoutAdvertisementSnippet.objects.filter(code=code).exclude(live=False).first()
        placements = [p.code for p in snippet.placements.all()]
        return dict(body=snippet.body, snippet=snippet,
                    gpt_disabled=context.get('is_gpt_disabled'),
                    request=context.get('request'),
                    utm_source=f"{snippet.code}",
                    placements=placements
                    )
    except:
        return dict(body=None)

@register.inclusion_tag('tags/conjugation_advert_head.html')
def conjugation_advertisement_head(code):
    try:
        return dict(head=PageLayoutAdvertisementSnippet.objects.filter(code=code).exclude(live=False)[0].head)
    except:
        return dict(head=None)
