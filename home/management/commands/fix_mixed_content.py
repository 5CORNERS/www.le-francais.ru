from re import search, sub, finditer
from urllib.parse import urlparse

from django.core.management import BaseCommand

from home.models import LessonPage, PageWithSidebar
from ._private import set_block


class Command(BaseCommand):
	def handle(self, *args, **options):
		fix_mixed_content_pages(PageWithSidebar)
		# fix_iframe_errors()

def fix_mixed_content_pages(PageModel):
	for page in PageModel.objects.all():
		for tab in (
				page.body,
				# page.comments_for_lesson,
				# page.dictionary,
		):
			for i in range(len(tab.stream_data)):
				block, is_find = check_block(get_block(tab, i))
				if is_find:
					set_block(i, block, tab)
					print('save page ' + page.slug + ' block ' + block.id)
					page.save()
		if PageModel == LessonPage:
			for i in range(len(page.other_tabs.stream_data)):
				tab = get_block(page.other_tabs, i)
				for j in range(len(tab.value['body'].stream_data)):
					block, is_find = check_block(get_block(tab.value['body'], j))
					if is_find:
						print('save page ' + page.slug + ' block ' + block.id)
						set_block(j, block, tab.value['body'])
						set_block(i, tab, page.other_tabs)
						page.save()



def get_block(stream_field, i):
	return stream_field.__getitem__(i)


def process_html(block):
	value = block.value
	if bool(search(r'http://', value)):
		block.value = sub('http://', '//', block.value)
		return block, True
	else:
		return block, False


def get_no_protocol(urlparse_object):
	return '//' + urlparse_object.netloc + urlparse_object.path


def process_audio(block):
	if not bool(search('http://', block.value['url'])):
		return block, False
	block.value['url'] = get_no_protocol(urlparse(block.value['url']))
	return block, True


def process_video(block):
	if not (bool(search('http://', block.value['source'])) | bool(search('http://', block.value['poster']))):
		return block, False
	block.value['source'] = get_no_protocol(urlparse(block.value['source']))
	block.value['poster'] = get_no_protocol(urlparse(block.value['poster']))
	return block, True


def process_document(block):
	if not bool(search('http://', block.value['url'])):
		return block, False
	block.value['url'] = get_no_protocol(urlparse(block.value['url']))
	return block, True


def process_paragraph(block):
	value = block.value
	if bool(search(r'http://', value)):
		block.value = sub('http://', '//', block.value)
		return block, True
	else:
		return block, False


def check_block(block):
	block_type = block.block_type
	if block_type == 'html':
		return process_html(block)
	if block_type == 'audio':
		return process_audio(block)
	if block_type == 'video':
		return process_video(block)
	if block_type == 'document':
		return process_document(block)
	# if block_type == 'paragraph':
	# 	return process_paragraph(block)
	return block, False

IFRAME_PATTERN = r"<iframe.+?(jujo00obo2o234ungd3t8qjfcjrs3o6k).+?>"

SRC_PATTERN = r'''src=".+?"'''

def fix_iframe_errors():
	for page in LessonPage.objects.all():
		for tab in (page.body, page.comments_for_lesson, page.dictionary):
			for i in range(len(tab.stream_data)):
				block, is_find = find_and_fix_iframe(get_block(tab, i))
				if is_find:
					print(page.slug + ' ' + block.id)
					set_block(i, block, tab)
					page.save()

def find_and_fix_iframe(block):
	iframe_list = []
	if block.block_type == 'html' and bool(search(IFRAME_PATTERN, block.value)):
		for iframe_match in finditer(IFRAME_PATTERN, block.value):
			s = int(iframe_match.start())
			e = int(iframe_match.end())
			src, src_s, src_e = get_substring(SRC_PATTERN, block.value[s:e])
			src = sub('http://jujo00obo', 'https://jujo00obo', src)
			iframe = block.value[s:e][:src_s] + src + block.value[s:e][src_e:]
			iframe_tuple = (s,iframe,e)
			iframe_list.append(iframe_tuple)
		for iframe in reversed(iframe_list):
			block.value = block.value[:iframe[0]] + iframe[1] + block.value[iframe[2]:]
		return block, True
	return block, False

def get_substring(pattern, string):
	match_object = search(pattern, string)
	substring_start, substring_end = int(match_object.start()), int(match_object.end())
	substring = string[substring_start:substring_end]
	return substring, substring_start, substring_end
