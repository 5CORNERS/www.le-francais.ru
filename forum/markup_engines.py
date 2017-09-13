from __future__ import unicode_literals, absolute_import

from django.forms import Textarea
from django.template import Context
from django.template.loader import get_template
from markdown import Markdown
from pybb.markup.markdown import MarkdownParser


class CustomMarkdownParser(MarkdownParser):
	def __init__(self):
		super(CustomMarkdownParser, self).__init__()
		self._parser = Markdown(
			extensions=[
				'markdown.extensions.nl2br',
				'pymdownx.extra',
				'pymdownx.magiclink',
				'pymdownx.emoji',
				'pymdownx.tasklist',
				'pymdownx.details',
				'pymdownx.superfences',
			],
			safe_mode='escape',
		)
