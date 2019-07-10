import csv
from io import TextIOWrapper

from django.conf.urls import url
from django.contrib import admin
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse

from home.models import LessonPage
from .models import Word, WordTranslation
from .forms import DictionaryCsvImportForm
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
			with transaction.atomic():
				for i, row in enumerate(reader):
					print('\r' + str(int(i / 3641 * 100)) + '%', end='')
					if row[0]:
						word = Word.objects.create(
							word=row[3],
							cd_id=int(row[0].split('.')[0]),
							genre=row[2] if row[2] == 'm' or row[2] == 'f' else None,
						)
						WordTranslation.objects.create(
							translation=row[4],
							word=word,
						)
						if row[1]:
							word.lessons.add(LessonPage.objects.get(lesson_number=row[1]))
			print('\nDone!')
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
