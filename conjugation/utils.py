from .models import Verb, Template

ENDINGS={}

def get_verb(verb_infinitive):
    try: 
        v = Verb.objects.get(infinitive=verb_infinitive)
    except:
        return "Verb does not exist"
    return v

def print_conjugations(v):
    t = v.template
    template_ending = dict(t.infinitive['infinitive-present'])['p']['i']
    verb_starting = v.infinitive.rstrip(template_ending)
    moods = [t.indicative,t.conditional,t.subjunctive,t.imperative,t.participle]
    for mood in moods:
        print('mood')
        for tense,table in mood:
            print('\t'+tense)
            for conjugation in table['p']:
                if isinstance(conjugation,dict):
                    verb = verb_starting+conjugation['i']
                    real_endings = ENDINGS[mood][tense]
                    print('\t\t'+verb)
    
            
    
    