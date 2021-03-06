from collections import OrderedDict

from django.core.management import BaseCommand

from le_francais_dictionary.models import Word
import csv
import operator

titles = [('NOL', 'order'),
          ('IDX', 'cd_id'),
          ('NO', 'packet.lesson.lesson_number'),
          ('PACK', 'packet.name'),
          ('WORD_UNIFIED', 'uni.word'),
          ('WORD_ORIG', 'word'),
          ('GROUP', 'definition_num'),
          ('GROUP_ID', 'group_id'),
          ('TRANSLATION_UNIFIED', 'uni.translation'),
          ('TRANSLATION_ORIG', 'first_translation.translation'),
          ('POS', 'part_of_speech'),
          ('GEN', 'genre'),
          ('RU-VOICE_UNI', 'uni.ru_filename'),
          ('FR-VOICE_UNI', 'uni.fr_filename'),
          ('RU-VOICE_ORIG', 'first_translation.filename'),
          ('FR-VOICE_ORIG', 'filename'), ]

def to_tsv(to_tsv_dict):
	keys =  to_tsv_dict[0].keys()
	with open('le_francais_dictionary/local/csv_table.csv', 'w', encoding='utf-8') as csv_file:
		dict_writer = csv.DictWriter(csv_file, keys, delimiter='\t')
		dict_writer.writeheader()
		dict_writer.writerows(to_tsv_dict)


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('-g', dest='group_ids', type=int, action='append')

	def handle(self, *args, **options):
		table = []
		l = Word.objects.all().count()
		q = Word.objects.prefetch_related(
				'packet',
				'packet__lesson',
				'wordtranslation_set',
				'group',
				'group__unifiedword_set'
		).order_by('order').all()
		if options['group_ids']:
			q = q.filter(group_id__in=options['group_ids'])
		for word in q:
			print(f'{word.order}/{l}\t{word}')
			row_dict = OrderedDict()
			for title, attr in titles:
				try:
					row_dict[title] = operator.attrgetter(attr)(word) or ''
				except Exception as err:
					row_dict[title] = 'ERROR'
					print(str(err))
			table.append(row_dict)
		to_tsv(table)


