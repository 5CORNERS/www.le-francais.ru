import xmltodict
import ast


def get_dicts():
    verbs_xml = open(file='conjugation\\data\\verbs-fr.xml',
                     mode='rb')
    conjugation_xml = open(
        file='conjugation\\data\\conjugation-fr.xml',
        mode='rb')

    verbs_dict = xmltodict.parse(verbs_xml,dict_constructor=dict)
    conjugation_dict = xmltodict.parse(conjugation_xml,dict_constructor=dict)
    return verbs_dict, conjugation_dict


from django.core.management import BaseCommand

from conjugation.models import Template, Verb

class Command(BaseCommand):
    def handle(self, *args, **options):
        verbs, templates = get_dicts()
        for template in templates['conjugation-fr']['template']:
            t = Template.objects.get(name=template['@name'])
            t.data = {
                'infinitive':template['infinitive'],
                'indicative':template['indicative'],
                'conditional':template['conditional'],
                'subjunctive':template['subjunctive'],
                'imperative':template['imperative'],
                'participle':template['participle']
            }
            print(t)
            t.save()