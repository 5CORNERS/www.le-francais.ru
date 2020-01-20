import csv
import os
from shutil import copyfile
from le_francais_dictionary.models import Word

def update_base():
	dir = 'D:/Sound/SoundF3/'
	with open('le_francais_dictionary/local/base_update.csv', encoding='utf-8') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			word = Word.objects.get(pk=row['IDX'])
			if not os.path.exists(dir + row['Filename']):
				print(row['IDX'], row['Filename'], "Can't find", sep=' ---- ')
			else:
				print(row['IDX'], row['Filename'], sep=' ---- ')
				word.word = row['Title']
				old_url = word._polly_url
				word._polly_url = old_url.rsplit('/', 1)[0] + '/' + row['Filename']
				print(old_url, '=>', word._polly_url)
				word.save()
