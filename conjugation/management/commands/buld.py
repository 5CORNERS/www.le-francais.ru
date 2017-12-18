import xmltodict


def get_dicts():
    verbs_xml = open(file='C:\\Users\\ilia.dumov\\PycharmProjects\\www.le-francais.ru\\conjugation\\data\\verbs-fr.xml',
                     mode='rb')
    conjugation_xml = open(
        file='C:\\Users\\ilia.dumov\\PycharmProjects\\www.le-francais.ru\\conjugation\\data\\conjugation-fr.xml',
        mode='rb')

    verbs_dict = xmltodict.parse(verbs_xml)
    conjugation_dict = xmltodict.parse(conjugation_xml)
    return verbs_dict, conjugation_dict


from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        verbs, conjugation = get_dicts()
