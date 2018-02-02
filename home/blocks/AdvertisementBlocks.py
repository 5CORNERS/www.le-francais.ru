from wagtail.wagtailcore.blocks import StructBlock
from wagtail.wagtailsnippets.blocks import SnippetChooserBlock
from wagtail.wagtailcore.blocks import BooleanBlock

from home.models import InlineAdvertisementSnippet


class AdvertisementInline(StructBlock):
    advertisement = SnippetChooserBlock(InlineAdvertisementSnippet)
    disable = BooleanBlock(required=False)

    class Meta:
        icon = 'snippet'
        label = 'Advert'
        template = 'blocks/advertisement_inline.html'
