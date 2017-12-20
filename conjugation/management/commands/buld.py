import xmltodict


def get_dicts():
    verbs_xml = open(file='C:\\Users\\ilia.dumov\\PycharmProjects\\www.le-francais.ru\\conjugation\\data\\verbs-fr.xml',
                     mode='rb')
    conjugation_xml = open(
        file='C:\\Users\\ilia.dumov\\PycharmProjects\\www.le-francais.ru\\conjugation\\data\\conjugation-fr.xml',
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
            Template.objects.create(
                name=template['@name'],
                infinitive=template['infinitive'],
                indicative=template['indicative'],
                conditional=template['conditional'],
                subjunctiv=template['subjunctive'],
                imperative=template['imperative'],
                participle=template['participle']
            )
        for verb in verbs['verbs-fr']['v']:
            verb_template = Template.objects.get(name=verb['t'])
            if 'aspirate-h' in verb:
                aspirate_h = True
            else:
                aspirate_h = False
            Verb.objects.create(
                infinitive=verb['i'],
                template=verb_template,
                aspirated_h = aspirate_h
            )