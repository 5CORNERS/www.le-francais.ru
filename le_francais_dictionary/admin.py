import csv
from io import TextIOWrapper

from django.conf.urls import url
from django.contrib import admin
from django.db import transaction
from django.shortcuts import redirect, render

from home.models import LessonPage
from .forms import DictionaryCsvImportForm
from .models import Word, WordTranslation


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
	ordering = ['cd_id']
	list_display = ['word']
	list_filter = ['genre']
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
			to_create = dict(
				words=[],
				translations=[],
				lesson_relations=[],
			)
			lesson_ids = dict(LessonPage.objects.values_list('lesson_number', 'id'))
			for i, row in enumerate(reader):
				if row[0]:
					print('\r' + str(
						int(i / 3641 * 100)), end='')
					word = Word(
						id=i,
						word=row[3],
						cd_id=row[0],
						genre=row[2] if row[2] in ['m','f'] else None,
						)
					translation = WordTranslation(
						word_id=i,
						translation=row[4]
					)
					lesson_relation = Word.lessons.through(
						word_id = i,
						lessonpage_id = lesson_ids[int(row[1])]
					) if row[1] else None
					to_create['words'].append(word)
					to_create['translations'].append(translation)
					to_create['lesson_relations'].append(lesson_relation)
			print('\nBulk creating words')
			Word.objects.bulk_create(
				[w for w in to_create['words']]
			)
			print('Bulk crating translations')
			WordTranslation.objects.bulk_create(
				[wt for wt in to_create['translations']]
			)
			print('Bulk creating relations')
			Word.lessons.through.objects.bulk_create(
				[wl for wl in filter(None.__ne__, to_create['lesson_relations'])]
			)
			print('Done!')
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
