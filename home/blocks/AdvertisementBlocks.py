from wagtail.wagtailcore.blocks import StructBlock
from wagtail.wagtailsnippets.blocks import SnippetChooserBlock

from home.models import AdvertisementSnippet


class AdvertisementInline(StructBlock):
    advertisement = SnippetChooserBlock(AdvertisementSnippet)

    class Meta:
        icon = 'snippet'
