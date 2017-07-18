from pybb.markup.markdown import MarkdownParser
from markdown import Markdown


class CustomMarkdownParser(MarkdownParser):

	def __init__(self):
		super(CustomMarkdownParser, self).__init__()
		self._parser = Markdown(
			extensions=[
				'pymdownx.extra',
				'pymdownx.magiclink',
				'pymdownx.emoji',
				'pymdownx.tasklist',
				'pymdownx.details',
				'pymdownx.superfences',
			],
			safe_mode='escape',
		)
