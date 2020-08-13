from django.core.management import BaseCommand

from conjugation.models import DeffectivePattern, Except

def2exept = {
    'indicative_compose_past':'indicative_composé-past',
    'indicative_anterieur_past':'indicative_antérieur-past',
    'indicative_pluperfect':'indicative_pluperfect',
    'indicative_anterieur_future':'indicative_antérieur-future',
    'subjunctive_past':'subjunctive_past',
    'subjunctive_pluperfect':'subjunctive_pluperfect',
    'conditional_past_first':'conditional_past_first',
    'conditional_past_second':'conditional_past_second',
    'imperative_past':'imperative_past',
    'infinitive_past':'infinitive_past',
    'gerund_past':'gerund_past',
}

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for defective_pattern in DeffectivePattern.objects.all():
            verbs = list(defective_pattern.verb_set.all())
            verb_names = [verb.infinitive for verb in verbs]
            exception = Except.objects.create(name=f'DefectivePattern:{str(verb_names):.50}')
            exception.verbs.add(*verbs)
            exception.save()
            for d_attr, e_attr in def2exept.items():
                setattr(exception, e_attr, getattr(defective_pattern, d_attr))
            print(defective_pattern)
