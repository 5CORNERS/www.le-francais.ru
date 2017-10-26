from re import search, sub
from urllib.parse import urlparse

from django.core.management import BaseCommand

from home.models import LessonPage
from ._private import set_block


class Command(BaseCommand):
	def handle(self, *args, **options):
		print_mixed_content_pages(LessonPage)


def print_mixed_content_pages(PageModel):
	for page in PageModel.objects.all():
		for tab in (page.body, page.comments_for_lesson, page.dictionary):
			for i in range(len(tab.stream_data)):
				block, is_find = check_block(get_block(tab, i))
				if is_find:
					set_block(i, block, tab)
					print('save page ' + page.slug + ' block ' + block.id)
					page.save()
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
