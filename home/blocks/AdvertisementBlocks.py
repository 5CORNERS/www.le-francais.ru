from wagtail.core.blocks import StructBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.core.blocks import BooleanBlock

from home.models import InlineAdvertisementSnippet


class AdvertisementInline(StructBlock):
    advertisement = SnippetChooserBlock(InlineAdvertisementSnippet)
    disable = BooleanBlock(required=False)

    class Meta:
        icon = 'snippet'
        label = 'Advert'
        template = 'blocks/advertisement_inline.html'
