"""
No follow links

Add html attribut to all links nofollow="true"
"""

import re
from urllib.parse import urlparse, urlunparse

from markdown.extensions import Extension
from markdown.inlinepatterns import util, dequote, LinkPattern, Pattern

NO_BRACKET = r'[^\]\[]*'

BRK = (
    r'\[(' +
    (NO_BRACKET + r'(\[') * 6 +
    (NO_BRACKET + r'\])*') * 6 +
    NO_BRACKET + r')\]'
)

NO_IMG = r'(?<!\!)'

LINK_RE = NO_IMG + BRK + \
          r'''\(\s*(<.*?>|((?:(?:\(.*?\))|[^\(\)]))*?)\s*((['"])(.*?)\12\s*)?\)'''

AUTOLINK_RE = r'<((?:[Ff]|[Hh][Tt])[Tt][Pp][Ss]?://[^>]*)>'


class NewLinkPattern(LinkPattern):
    """ Return a link element from the given match. """

    def handleMatch(self, m):
        el = util.etree.Element("a")
        el.text = m.group(2)
        title = m.group(13)
        href = m.group(9)

        if href:
            if href[0] == "<":
                href = href[1:-1]
            el.set("href", self.sanitize_url(self.unescape(href.strip())))
        else:
            el.set("href", "")

        if bool(re.search('(\/\/)', href)):
            rel = "nofollow"
            target = "_blank"
            el.set("rel", rel)
            el.set("target", target)
        else:
            target = "_self"
            el.set("target", target)

        if title:
            title = dequote(self.unescape(title))
            el.set("title", title)
        return el

    def sanitize_url(self, url):
        """
        Sanitize a url against xss attacks in "safe_mode".

        Rather than specifically blacklisting `javascript:alert("XSS")` and all
        its aliases (see <http://ha.ckers.org/xss.html>), we whitelist known
        safe url formats. Most urls contain a network location, however some
        are known not to (i.e.: mailto links). Script urls do not contain a
        location. Additionally, for `javascript:...`, the scheme would be
        "javascript" but some aliases will appear to `urlparse()` to have no
        scheme. On top of that relative links (i.e.: "foo/bar.html") have no
        scheme. Therefore we must check "path", "parameters", "query" and
        "fragment" for any literal colons. We don't check "scheme" for colons
        because it *should* never have any and "netloc" must allow the form:
        `username:password@host:port`.

        """
        if not self.markdown.safeMode:
            # Return immediately bipassing parsing.
            return url

        try:
            scheme, netloc, path, params, query, fragment = url = urlparse(url)
        except ValueError:  # pragma: no cover
            # Bad url - so bad it couldn't be parsed.
            return ''

        locless_schemes = ['', 'mailto', 'news']
        allowed_schemes = locless_schemes + ['http', 'https', 'ftp', 'ftps']
        if scheme not in allowed_schemes:
            # Not a known (allowed) scheme. Not safe.
            return ''

        if netloc == '' and scheme not in locless_schemes:  # pragma: no cover
            # This should not happen. Treat as suspect.
            return ''

        # Wikipedia is using colons it their urls

        # for part in url[2:]:
        #     if ":" in part:
        #         # A colon in "path", "parameters", "query"
        #         # or "fragment" is suspect.
        #         return ''

        # Url passes all tests. Return url as-is.
        return urlunparse(url)


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
