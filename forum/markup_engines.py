from __future__ import unicode_literals, absolute_import

from django.forms import Textarea
from django.template import Context
from django.template.loader import get_template
from markdown import Markdown
from pybb.markup.markdown import MarkdownParser


import pymdownx.keys

if not hasattr(pymdownx.keys.KeysPattern, '_orig_process_key'):
	pymdownx.keys.KeysPattern._orig_process_key = pymdownx.keys.KeysPattern.process_key

def _custom_process_key(self, key):
	val = self._orig_process_key(key)
	if val is not None:
		return val
	clean_key = key.strip('"\' \t')
	if clean_key:
		return (None, clean_key)
	return None

pymdownx.keys.KeysPattern.process_key = _custom_process_key

pymdownx.keys.RE_KBD = r'''(?x)
(?:
    # Escape
    (?<!\\)(?P<escapes>(?:\\{2})+)(?=\+)|
    # Key
    (?<!\\)\+{2}
    (
        (?:(?:[^\+\r\n]+?|"(?:\\.|[^"])+"|\'(?:\\.|[^\'])+\')\+)*?
        (?:[^\+\r\n]+?|"(?:\\.|[^"])+"|\'(?:\\.|[^\'])+\')
    )
    \+{2}
)
'''


class CustomMarkdownParser(MarkdownParser):
	def __init__(self):
		super(CustomMarkdownParser, self).__init__()
		self._parser = Markdown(
			extensions=[
				'forum.customextensions.nofollowlinks',
				'markdown.extensions.nl2br',
				'markdown.extensions.smarty',
				'pymdownx.extra',
				'pymdownx.emoji',
				'pymdownx.tasklist',
				'pymdownx.details',
				'pymdownx.superfences',
				'pymdownx.tilde',
				'pymdownx.caret',
				'pymdownx.keys',
				'pymdownx.mark',
				'pymdownx.smartsymbols',
			],
			safe_mode='escape',
		)

	def quote(self, text, username=''):
		cleaned = text.replace('\r\n', '\n').replace('\r', '\n')
		quoted_lines = '\n> '.join(cleaned.split('\n'))
		if username:
			return '> **' + username + '**:\n> ' + quoted_lines + '\n\n'
		return '> ' + quoted_lines + '\n\n'
