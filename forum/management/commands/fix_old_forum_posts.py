import re

import html2text
import lxml.html
from django.utils.html import strip_tags

from django.core.management import BaseCommand
from pybb.models import Post, Topic, Forum, Category

class Command(BaseCommand):
	def handle(self, *args, **options):
		category = Category.objects.get(name="Old")
		for forum in category.forums.all():
			for topic in forum.topics.all():
				for post in topic.posts.all():
					print('\nCategory: %s\nForum: %s\nTopic: %s\nPost: %s'% (category.name, forum.name, topic.id, post.id))
					fix_post(post)


def fix_post(post):
	post.body = text_decode(post.body)
	post.body = hide_emails(post.body)
	print(post.body)

def text_decode(text: str):
	if is_utf(text):
		text = text.encode().decode('unicode-escape')
	if is_html(text):
		body = html2text.html2text(text)
	else:
		body = text
	return body


def is_utf(text):
	regex = re.compile(r'(\\\\u([a-z]|[0-9]){4})')
	return re.match(regex, text)


def is_html(text):
	return lxml.html.fromstring(text).find('.//*') != None


def hide_emails(text):
	regex = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
	emails = regex.findall(text)
	for email in emails:
		email = re.sub(r"(.+(?=\@))", "[hidden]", email)
		text = re.sub(regex, email, text, 1)
	return text

def spoiler_bloquote():
	regex = re.compile(r'^.{0,}(wrote|escribió|написал|écrit|йcrit|):$')
