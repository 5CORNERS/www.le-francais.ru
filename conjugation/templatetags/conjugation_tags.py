from django import template
from django.urls import reverse

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