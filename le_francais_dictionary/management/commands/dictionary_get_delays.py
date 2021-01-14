import argparse

from django.core.management import BaseCommand
from django.utils import timezone

from le_francais_dictionary.models import UserWordData

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-y', dest='year', type=int)
        parser.add_argument('-m', dest='month', type=int)
        parser.add_argument('-d', dest='day', type=int)
        parser.add_argument('-u', dest='username', type=str)
        parser.add_argument('-g', dest='grade', type=str2bool, default=None)

    def handle(self, *args, **options):
        if options['year'] and options['month'] and options['day']:
            initial_datetime = timezone.datetime(options['year'], options['month'], options['day'])
        else:
            initial_datetime = timezone.datetime(2020, 3, 17)
        s = 'ID\tDATETIME\tUSER_ID\tUSERNAME\tWORD\tWORD_ID\tY/N\tDELAY\tUNCOVERED\n'
        q = UserWordData.objects.prefetch_related('word', 'user').filter(datetime__gte=initial_datetime)
        if options['username']:
            q = q.filter(user__username=options['username'])
        if options['grade'] is not None:
            q = q.filter(grade=options['grade'])
        for data in q:
            line = f'{data.id}\t{data.datetime.strftime("%m-%d-%Y %H:%M:%S")}\t' \
                   f'{data.user_id}\t{data.user.username}\t{data.word_id}\t{data.word.word}\t' \
                   f'{data.grade}\t{data.delay}\t{data.mistakes}'
            print(line)
            s += line + '\n'
        open('temp.tsv', 'w', encoding='utf-8').write(s)
