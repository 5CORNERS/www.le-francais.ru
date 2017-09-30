import re

import bs4
from django.core.management import BaseCommand

from home.models import LessonPage
from ._private import set_block


class Command(BaseCommand):
	def handle(self, *args, **options):
		# for page in LessonPage.objects.all():
		# 	self.del_lang(page).save()
		# self.span_fix(LessonPage)
		# self.span_fix(PageWithSidebar)
		# self.del_comments(LessonPage)
		# self.replace_img(LessonPage)
		# self.replace_img(PageWithSidebar)
		# 
		# self.fix_span_in_transcript()
		self.del_pdf_iframe()

	def del_pdf_iframe(self):
		for page in LessonPage.objects.all():
			for i in range(len(page.body.stream_data)):
				block = page.body.__getitem__(i)
				if block.block_type == 'html':
					soup = bs4.BeautifulSoup(block.value, "html5lib")
					pdf_elements = soup.find_all(name='div', attrs={'class': 'sites-embed-border-on sites-embed'})
					self.stdout.write('Номер урока '+str(page.lesson_number)+' ' + str(pdf_elements.__len__()))
					for pdf_element in pdf_elements:
						for child in pdf_element.contents:
							if child.name == 'h4' and child.string.find('Конспект') != -1:
								pdf_element.decompose()
					block.value = str(soup)
					set_block(i, block, page.body)
			page.save()


	def span_fix(self, PageModel):
		# for page in PageModel.objects.all():
		# 	if page.lesson_number < 135:
		page = LessonPage.objects.get(lesson_number=24)
		print('Lesson_number ' + str(page.lesson_number))
		for i in range(len(page.body.stream_data)):
			block = page.body.__getitem__(i)
			if block.block_type == 'html':
				new_value = self.replace(block.value)
				block.value = new_value
				set_block(i, block, page.body)
		page.save()

	def replace(self, value):
		new_value = value
		new_value = re.sub(r'((\n|\s+)<font)', '<font', new_value)
		new_value = re.sub(r'((\n|\s+)<\/font>)', '</font>', new_value)
		new_value = re.sub(r'((\n|\s+)<span)', '<span', new_value)
		new_value = re.sub(r'((\n|\s+)<\/span>)', '</span>', new_value)
		new_value = re.sub(r'((\n|\s+)<a)', '<a', new_value)
		new_value = re.sub(r'((\n|\s+)<\/a>)', '</a>', new_value)
		new_value = re.sub(r'((\n|\s+)<p)', '<p', new_value)
		new_value = re.sub(r'((\n|\s+)<\/p>)', '</p>', new_value)
		new_value = re.sub(r'((\n|\s+)<\/b>)', '</b>', new_value)
		new_value = re.sub(r'((\n|\s+)<\/i>)', '</i>', new_value)
		new_value = re.sub(r'<b>\s+\n\s+', '<b>', new_value)
		new_value = re.sub(r'<i>\s+\n\s+', '<i>', new_value)

		list = re.findall(r'<span[^>]+>\s+\n\s+', new_value)
		trim_list = []
		for span in list:
			new_span = re.sub(r'\s+\n\s+', '', span)
			trim_list.append(new_span)
			new_value = new_value.replace(span, new_span)
		list = re.findall(r'<span[^>]+>\s+', new_value)
		trim_list = []
		for span in list:
			new_span = span.strip()
			trim_list.append(new_span)
			new_value = new_value.replace(span, new_span)
		return new_value

	def del_comments(self, PageModel):
		doc = '''<div>*****</div'''
		for page in PageModel.objects.all():
			is_find = False
			for i in range(len(page.body.stream_data)):
				block = page.body.__getitem__(i)
				if block.block_type == 'html':
					value = block.value
					is_find = block.value.find(doc)
					if is_find != -1 or is_find != False:
						new_value = block.value.replace(doc, '<div>*****</div>')
						block.value = new_value
						set_block(i, block, page.body)
			print(str(page.title) + ' ' + str(is_find))
			page.save()

	def fix_span_in_transcript(self):
		for page in LessonPage.objects.all():
			if 44 < page.lesson_number:
				for i in range(len(page.body.stream_data)):
					block = page.body.__getitem__(i)
					if block.block_type == 'html':
						value = block.value
						# print(re.findall(r".{1,10}(?<!\s|’|')<span.{1,10}", block.value))
						new_value = re.sub(r"(?<!\s|’|')<span", ' <span', value)
						block.value = new_value
					set_block(i, block, page.body)
				page.save()

	def replace_img(self, PageModel):
		exts = {
			r'(MP3|mp3)': 'mp3',
			r'(MSW|msw)': 'msw',
			r'(PDF|pdf)': 'pdf',
			r'(BX|bx)': 'bx',
			r'(MOVIEICON|movieicon)': 'movieicon',
			r'(DOWNLOAD|download)': 'download',
		}
		for page in PageModel.objects.all():
			for i in range(len(page.body.stream_data)):
				block = page.body.__getitem__(i)
				if block.block_type == 'html':
					new_value = block.value
					for ext in exts:
						print('Replacing ' + 'Page ' + str(page.slug) + ' Block ' + str(i) + ' Ext ' + str(
							ext) + '::' + str(re.findall(
							r'''(<a.+''' + ext + '''.(PNG|png)[\s\S]+?<img.+?src=\".+sites.+''' + ext + '''.(PNG|png)[\s\S]+?<\/a>)''',
							new_value)
						))
						new_value = re.sub(
							r'''(<a.+''' + ext + '''.(PNG|png)[\s\S]+?<img.+?src=\".+?''' + ext + '''.(PNG|png)[\s\S]+?<\/a>)''',
							'<img border="0" src="//files.le-francais.ru/photos/illustrations/' + exts[ext] + '.png"/>',
							new_value
						)
					block.value = new_value
					set_block(i, block, page.body)
			page.save()

	def delete_img_href(self, PageModel):
		pass

	def del_lang(self, page):
		for i in range(len(page.body.stream_data)):
			block = page.body.__getitem__(i)
			if block.block_type == 'html':
				value = block.value
				soup1 = bs4.BeautifulSoup(value, 'html.parser')
				for match in soup1.findAll('span', lang=True):
					match.unwrap()
				block.value = soup1
				set_block(i, block, page.body)
		return page
