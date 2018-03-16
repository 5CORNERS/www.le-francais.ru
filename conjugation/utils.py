from .models import Verb as V

ENDINGS = {}


def get_verb(verb_infinitive):
    try:
        v = V.objects.get(infinitive=verb_infinitive)
    except:
        return "Verb does not exist"
    return v


def get_conjugations(v):
    d = {}
    t = v.template
    template_ending = t.data['infinitive']['infinitive-present']['p']['i']
    verb_starting = v.infinitive.rstrip(template_ending)
    for mood, mood_value in t.data.items():
        d[mood] = {}
        for tense, endings in mood_value.items():
            d[mood][tense] = []
            for end in endings['p']:
                if isinstance(end, dict):
                    d[mood][tense].append((verb_starting, end['i']))
    return d
