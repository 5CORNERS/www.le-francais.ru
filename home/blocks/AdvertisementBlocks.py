from wagtail.wagtailcore.blocks import StructBlock
from wagtail.wagtailsnippets.blocks import SnippetChooserBlock

from home.models import InlineAdvertisementSnippet


class AdvertisementInline(StructBlock):
    advertisement = SnippetChooserBlock(InlineAdvertisementSnippet)

    class Meta:
        icon = 'snippet'
        label = 'Advert'
        template = 'blocks/advertisement_inline.html'
