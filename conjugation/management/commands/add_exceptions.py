from django.core.management import BaseCommand
from conjugation.models import Verb, Except


class Command(BaseCommand):
    def handle(self, *args, **options):

        exception_appeler, created_appeler = Except.objects.get_or_create(
            name="ellé -> elé"
        )
        exception_appeler.question = True
        exception_appeler.question_pronominal = True
        exception_appeler.question_negation = True
        exception_appeler.question_pronominal_negation = True
        exception_appeler.indicative_present = True
        exception_appeler.person_1 = True
        exception_appeler.pattern_verb = r'el<i>l</i><b>é</b>$'
        exception_appeler.replace_to_verb = 'el<b>é</b>'
        exception_appeler.order = 1

        exception_appeler2, created_appeler2 = Except.objects.get_or_create(
            name='ellé -> elle'
        )
        exception_appeler2.pronominal = True
        exception_appeler2.pronominal_negation = True
        exception_appeler2.negation = True
        exception_appeler2.indicative = True
        exception_appeler2.person_1 = True
        exception_appeler2.pattern_verb = r'el<i>l</i><b>é</b>$'
        exception_appeler2.replace_to_verb = 'el<i>l</i><b>e</b>'
        exception_appeler2.order = 2

        for verb in Verb.objects.filter(template__name='app:eler'):
            print(verb)
            exception_appeler.verbs.add(verb)
            exception_appeler2.verbs.add(verb)
        exception_appeler.save()
        exception_appeler2.save()

        exception_peler, created = Except.objects.get_or_create(
            name='èlé -> elé'
        )
        exception_peler.question = True
        exception_peler.question_negation = True
        exception_peler.negation = True
        exception_peler.indicative_present = True
        exception_peler.person_1 = True
        exception_peler.pattern_verb = r'<i>è</i>l<b>é</b>$'
        exception_peler.replace_to_verb = '<i>e</i>l<b>é</b>'
        for verb in Verb.objects.filter(template__name='p:eler'):
            print(verb)
            exception_peler.verbs.add(verb)
        exception_peler.save()

        exception_jeter, created_jeter = Except.objects.get_or_create(
            name='etté -> eté',
            pronominal=True,
            question=True,
            negation=True,
            question_pronominal=True,
            pronominal_negation=True,
            question_negation=True,
            question_pronominal_negation=True,
            indicative_present=True,
            person_1=True,
            pattern_verb=r'et<i>t</i><b>é</b>$',
            replace_to_verb='et<b>é</b>',
        )
        for verb in Verb.objects.filter(template__name='j:eter'):
            exception_jeter.verbs.add(verb)
        exception_jeter.save()

        exception_acheter, created_acheter = Except.objects.get_or_create(
            name='èté -> eté',
            question=True,
            question_negation=True,
            person_1=True,
            pattern_verb=r'<i>è</i>t<b>é</b>$',
            replace_to_verb='et<b>é</b>',
        )
        for verb in Verb.objects.filter(template__name='ach:eter'):
            exception_acheter.verbs.add(verb)
        exception_acheter.save()

        verbs_parler = [
            "plaire",
            "complaire",
            "déplaire",
            "rire",
            "convenir",
            "nuire",
            "mentir",
            "ressembler",
            "sourire",
            "suffire",
            "survivre",
            "acheter",
            "succéder",
            "téléphoner",
            "parler",
            "demander",
            "ntre-nuire",
            'dire',
            'ecrire'
        ]

        exceptions_parler, created = Except.objects.get_or_create(
            name='parler verbs'
        )
        exceptions_parler.pronominal = True
        exceptions_parler.question_pronominal = True
        exceptions_parler.pronominal_negation = True
        exceptions_parler.question_pronominal_negation = True
        exceptions_parler.indicative_composé_past = True
        exceptions_parler.indicative_pluperfect = True
        exceptions_parler.indicative_antérieur_past = True
        exceptions_parler.indicative_antérieur_future = True
        exceptions_parler.subjunctive_past = True
        exceptions_parler.subjunctive_pluperfect = True
        exceptions_parler.conditional_past_first = True
        exceptions_parler.person_4 = True
        exceptions_parler.person_5 = True
        exceptions_parler.person_6 = True
        exceptions_parler.conjugation_override = 'VERB_PAST_PARTICIPLE_S_M'
        for verb in Verb.objects.filter(infinitive__in=verbs_parler):
            exceptions_parler.verbs.add(verb)
        exceptions_parler.save()
