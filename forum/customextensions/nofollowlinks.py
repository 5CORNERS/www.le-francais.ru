"""
No follow links

Add html attribut to all links nofollow="true"
"""

from markdown.extensions import Extension
from markdown.inlinepatterns import util, dequote, LinkPattern, Pattern

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

AUTOLINK_RE = r'<((?:[Ff]|[Hh][Tt])[Tt][Pp][Ss]?://[^>]*)>'


class NewLinkPattern(LinkPattern):
	""" Return a link element from the given match. """

	def handleMatch(self, m):
		el = util.etree.Element("a")
		el.text = m.group(2)
		title = m.group(13)
		href = m.group(9)
		rel = "nofollow"
		target = "_blank"
		el.set("rel", rel)
		el.set("target", target)

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


class NewAutolinkPattern(Pattern):
	""" Return a link Element given an autolink (`<http://example/com>`). """

	def handleMatch(self, m):
		el = util.etree.Element("a")
		el.set('href', self.unescape(m.group(2)))
		el.set('rel', 'nofollow')
		target = "_blank"
		el.set("target", target)
		el.text = util.AtomicString(m.group(2))
		return el


class NoFollowLinksExtension(Extension):
	def extendMarkdown(self, md, md_globals):
		link = NewLinkPattern(LINK_RE, md)
		autolink = NewAutolinkPattern(AUTOLINK_RE, md)
		md.inlinePatterns['link'] = link
		md.inlinePatterns['autolink'] = autolink


def makeExtension(*args, **kwargs):
	return NoFollowLinksExtension(*args, **kwargs)
