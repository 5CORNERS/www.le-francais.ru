import os
import re

from django.core.management import BaseCommand

from home.models import LessonPage, PageWithSidebar, ArticlePage
from wagtail.core.models import Page as WagtailPage, PageBase
from ._private import set_block

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('arg', type=str, nargs='+')
		parser.add_argument(
			'--put',
			action='store_true',
			dest='push',
			default=False,
			help='push html from file back to site',
		)
		parser.add_argument(
			'--get',
			action='store_true',
			dest='get',
			default=False,
			help='get html from page and store it in file'
		)
		parser.add_argument('--slug', action='store_true', dest='slug',
		                    default=False)

	def handle(self, *args, **options):
		if options['slug']:
			for slug in options['arg']:
				if options['push']:
					self.from_html_page(slug)
				elif options['get']:
					self.to_html_page(slug)
		elif options['arg'][0] == 'all':
			if options['push']:
				self.from_html_all_lecons()
			elif options['get']:
				self.to_html_all_lecons()
		elif options['arg'][0] == 'all-2':
			if options['push']:
				self.from_html_all_pages()
			elif options['get']:
				self.to_html_all_pages()
		else:
			for num in options['arg']:
				if options['push']:
					self.from_html_lecon(num)
				elif options['get']:
					self.to_html_lecon(num)

	def from_html_page(self, slug):
		page = self.get_page_by_slug(slug)
		if page:
			self.write_blocks_to_page(
				blocks=self.read_file('html_files\\' + page.slug + '.html'),
				page=page
			)
		else:
			pass

	def to_html_page(self, slug):
		page = self.get_page_by_slug(slug)
		if page:
			html = self.read_page_body(page)
			self.write_to_file(page.slug, html)
		else:
			pass

	def to_html_all_lecons(self):
		for page in LessonPage.objects.all():
			html = self.read_page(page)
			self.write_to_file(self.sortable(page.slug), html)

	def from_html_all_lecons(self):
		file_names = os.listdir('html_files')
		for file_name in file_names:
			if file_name.split('-')[0] == 'lecon' and int(
					file_name.split('-')[1].split('.')[0]) < 134:
				slug = self.unsortable(file_name).rstrip('.html')
				self.write_blocks_to_page(
					blocks=self.read_file('html_files\\' + file_name),
					page=LessonPage.objects.get(slug=slug)
				)

	def to_html_all_pages(self):
		for page in WagtailPage.objects.filter(live=True):
			try:
				if not page.specific.is_selectable:
					continue
			except AttributeError:
				continue
			print(page.slug + '......', end='')
			if isinstance(page.specific, LessonPage):
				self.to_html_lecon(page.specific.lesson_number)
				print('Done')
			else:
				try:
					page.specific.body
				except:
					print('Error!')
					continue
				self.to_html_page(page.slug)
				print('Done')

	def from_html_all_pages(self):
		for fname in os.listdir('html_files'):
			print(fname)
			if fname.split('-')[0] == 'lecon' and int(
					fname.split('-')[1].split('.')[0]) < 136:
				slug = self.unsortable(fname).rstrip('.html')
				self.write_blocks_to_page(
					blocks=self.read_file('html_files\\' + fname),
					page=LessonPage.objects.get(slug=slug)
				)
			elif fname.endswith('.html') and not fname.split('-')[0] == 'lecon':
				slug = fname.rstrip('.html')
				self.from_html_page(slug)

	def from_html_lecon(self, num):
		page = self.get_page_by_number(num)
		self.write_blocks_to_page(
			blocks=self.read_file(
				'html_files\\' + self.sortable(page.slug) + '.html'),
			page=page
		)

	def to_html_lecon(self, num):
		page = self.get_page_by_number(num)
		html = self.read_page(page)
		self.write_to_file(self.sortable(page.slug), html)

	def write_blocks_to_page(self, blocks, page):
		for block in blocks['comments']:
			if block['type'] == 'html':
				try:
					new_block = page.comments_for_lesson.__getitem__(
						block['i'])
				except:
					pass
				new_block.value = block['value']
				set_block(block['i'], new_block, page.comments_for_lesson)
		for block in blocks['body']:
			if block['type'] == 'html':
				new_block = page.body.__getitem__(block['i'])
				new_block.value = block['value']
				set_block(block['i'], new_block, page.body)
		for block in blocks['dictionary']:
			if block['type'] == 'html':
				new_block = page.dictionary.__getitem__(block['i'])
				new_block.value = block['value']
				set_block(block['i'], new_block, page.dictionary)
		page.save_revision().publish()

	def read_page_body(self, page):
		doc = '\n<!--TAB_BODY--><br><a name="tab_body"></a><br>\n'
		for i in range(len(page.body.stream_data)):
			block = page.body.__getitem__(i)
			num = '0' + str(i) if i < 10 else str(i)
			if block.block_type == 'html':
				doc = doc + '\n<!--BLOCK_HTML_' + num + '-->\n' + block.value.replace(
					'\r\n', '\n')
			elif block.block_type == 'paragraph':
				doc = doc + '\n<!--BLOCK_PRGF_' + num + '-->\n'
			elif block.block_type == 'audio':
				doc = doc + '\n<!--BLOCK_AUDI_' + num + '-->\n'
			elif block.block_type == 'advertisement':
				doc = doc + '\n<!--BLOCK_SNPT_' + num + '-->\n'
		doc = doc + '\n<!--TAB_BODY_END--><br><a name="tab_body_end"></a><br>\n'
		return doc

	def read_page_comments(self, page):
		doc = '\n<!--TAB_COMMENTS--><br><a name="tab_comments"></a><br>\n'
		for i in range(len(page.comments_for_lesson.stream_data)):
			block = page.comments_for_lesson.__getitem__(i)
			num = '0' + str(i) if i < 10 else str(i)
			if block.block_type == 'html':
				doc = doc + '\n<!--BLOCK_HTML_' + num + '-->\n' + block.value
		doc = doc + '\n<!--TAB_COMMENTS_END--><br><a name="tab_comments_end"></a><br>\n'
		return doc

	def read_page_dictionary(self, page):
		doc = '\n<!--TAB_DICTIONARY--><br><a name="tab_dictionary"></a><br>\n'
		for i in range(len(page.dictionary.stream_data)):
			block = page.dictionary.__getitem__(i)
			num = '0' + str(i) if i < 10 else str(i)
			if block.block_type == 'html':
				doc = doc + '\n<!--BLOCK_HTML_' + num + '-->\n' + block.value
		doc = doc + '\n<!--TAB_DICTIONARY_END--><br><a name="tab_dictionary_end"></a><br>\n'
		return doc

	def read_page(self, page):
		return self.read_page_comments(page) + self.read_page_body(
			page) + self.read_page_dictionary(page)

	def write_to_file(self, file_name, doc):
		file_path = 'html_files\\' + file_name + '.html'
		with open(file_path, 'w', encoding='utf-8') as f:
			f.writelines(doc)

	def read_file(self, file_path):
		re_blocks = {'comments':[], 'dictionary':[], 'body':[]}
		with open(file_path, 'r', encoding='utf-8') as f:
			text = f.read()
		text = re.sub('^\n$', '', text, flags=re.MULTILINE)
		for tab_match in re.finditer(r'<!--TAB_(?P<type>[A-Z]+?)--><br><a name="\w+?"></a><br>(?P<tab>[\s\S]+?)<!--TAB_(?P<type_end>[A-Z]+?)_END-->.+?\n', text):
			if not tab_match:
				continue
			tab_type = tab_match.group('type').lower()
			if tab_match.group('type') != tab_match.group('type_end'):
				print('ERROR! missing closing tab comment')
			for block_match in re.finditer(r'<!--BLOCK_(?P<type>\w+?)_(?P<index>\d{2})-->(?P<content>[\s\S]+?)(?=(<!--BLOCK)|$)', tab_match.group('tab')):
				if block_match.group('type') is None:
					continue
				block_type = block_match.group('type').lower()
				index = int(block_match.group('index'))
				content = block_match.group('content')
				if not tab_type in re_blocks.keys():
					re_blocks[tab_type] = []
				re_blocks[tab_type].append({
					'type': block_type,
					'value': content,
					'i': index
				})
		return re_blocks

	def get_page_by_number(self, num):
		return LessonPage.objects.get(lesson_number=num)

	def get_page_by_slug(self, slug):
		if WagtailPage.objects.filter(slug=slug, live=True).exists():
			wagtail_page = WagtailPage.objects.filter(slug=slug, live=True)[0]
			return wagtail_page.specific
		else:
			return None
		# try:
		# 	return LessonPage.objects.get(slug=slug)
		# except LessonPage.DoesNotExist:
		# 	try:
		# 		return PageWithSidebar.objects.get(slug=slug)
		# 	except PageWithSidebar.DoesNotExist:
		# 		return ArticlePage.objects.get(slug=slug)

	def sortable(self, file_name: str):
		self.stdout.write(file_name)
		return 'lecon-' + '{0:03}'.format(
			int(file_name.split('-')[1].rstrip('.html')))

	def unsortable(self, sortable_file_name: str):
		return 'lecon-' + str(
			int(sortable_file_name.split('-')[1].split('.')[0])) + '.html'


def read_file_2(file):
	blocks = {'comments_for_lesson': [], 'body': [], 'dictionary': []}
