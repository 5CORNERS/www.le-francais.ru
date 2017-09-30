"""
No follow links

Add html attribut to all links nofollow="true"
"""

from markdown.extensions import Extension
from markdown.inlinepatterns import util, dequote, LinkPattern

NOBRACKET = r'[^\]\[]*'

BRK = (
	r'\[(' +
	(NOBRACKET + r'(\[') * 6 +
	(NOBRACKET + r'\])*') * 6 +
	NOBRACKET + r')\]'
)

NOIMG = r'(?<!\!)'

LINK_RE = NOIMG + BRK + \
          r'''\(\s*(<.*?>|((?:(?:\(.*?\))|[^\(\)]))*?)\s*((['"])(.*?)\12\s*)?\)'''


class NewLinkPattern(LinkPattern):
	""" Return a link element from the given match. """

	def handleMatch(self, m):
		el = util.etree.Element("a")
		el.text = m.group(2)
		title = m.group(13)
		href = m.group(9)
		rel = "nofollow"
		el.set("rel", rel)

		if href:
			if href[0] == "<":
				href = href[1:-1]
			el.set("href", self.sanitize_url(self.unescape(href.strip())))
		else:
			el.set("href", "")

		if title:
			title = dequote(self.unescape(title))
			el.set("title", title)
		return el


class NoFollowLinksExtension(Extension):
	def extendMarkdown(self, md, md_globals):
		link = NewLinkPattern(LINK_RE, md)
		md.inlinePatterns['link'] = link


def makeExtension(*args, **kwargs):
	return NoFollowLinksExtension(*args, **kwargs)
