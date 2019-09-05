import csv
from io import TextIOWrapper
from typing import List

from django.conf.urls import url
from django.contrib import admin
from django.db import transaction
from django.shortcuts import redirect, render

from home.models import LessonPage
from .forms import DictionaryCsvImportForm
from .models import Word, WordTranslation, Packet


# Register your models here.


def create_polly_task(modeladmin: admin.ModelAdmin, request, qs):
	for p in qs:
		p.create_polly_task()

class WordTranslationInline(admin.TabularInline):
	readonly_fields = ['polly']
	model = WordTranslation

	actions = [create_polly_task]

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
	change_list_template = 'dictionary/admin/change_list.html'
	list_display = ['cd_id', 'word', 'genre', 'part_of_speech', 'plural']
	ordering = ['id']
	list_filter = ['genre', 'part_of_speech', 'plural']
	list_select_related = []
	readonly_fields = ['polly']
	inlines = [WordTranslationInline]
	actions = [create_polly_task]

	def get_urls(self):
		urls = super(WordAdmin, self).get_urls()
		my_urls = [
			url('^import_csv/$', self.admin_site.admin_view(self.import_csv_view)),
		]
		return my_urls + urls

	def import_csv_view(self, request):
		if request.method == 'POST':
			form = DictionaryCsvImportForm(request.POST, request.FILES)
			if not form.is_valid():
				self.message_user(request, 'Form is not valid')
				return redirect('admin:le_francais_dictionary_word_changelist')
			csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8', errors='replace')
			reader = csv.reader(csv_file)

			words_to_create: List[Word] = []
			translations_to_create: List[WordTranslation] = []
			packets_to_create:List[Packet] = []

			packets_count = 1
			lesson_ids = dict(LessonPage.objects.values_list('lesson_number', 'id'))

			for i, row in enumerate(reader, 1):
				if i==1:
					continue
				if row[1]:
					if int(row[1]) > 20 and request.POST.get('test', False):
						continue
					genre = row[5].split(',')[0] if row[5] else None
					plural = True if row[5].split(',')[
						                 -1].strip() == 'pl' else False
					locution = True if 'loc' in row[4] else False
					if locution:
						part_of_speech = 'loc'
					else:
						part_of_speech = row[4].split(' ')[0]

					# Getting or creating new packet object
					packet = next((x for x in packets_to_create if
					               x.name == 'урок ' + row[1]), None)
					if packet is None:
						packet = Packet(
							id=packets_count,
							name='урок ' + row[1],
							lesson_id=lesson_ids[int(row[1])]
						)
						packets_to_create.append(packet)
						packets_count += 1

					word = Word(
						id=i,
						packet_id=packet.id,
						word=row[2],
						cd_id=row[0],
						genre=genre,
						plural = plural,
						part_of_speech=part_of_speech
						)
					translation = WordTranslation(
						word_id=i,
						translation=row[3]
					)

					words_to_create.append(word)
					translations_to_create.append(translation)

			Packet.objects.bulk_create(
				packets_to_create
			)
			Word.objects.bulk_create(
				words_to_create
			)
			WordTranslation.objects.bulk_create(
				translations_to_create
			)

			self.message_user(request, 'CSV file has been imported')
			return redirect('admin:le_francais_dictionary_word_changelist')
		form = DictionaryCsvImportForm()
		context = dict(
			self.admin_site.each_context(request),
			form = form,
		)
		return render(
			request, 'dictionary/admin/csv_form.html', context
		)
