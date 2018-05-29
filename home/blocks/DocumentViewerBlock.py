from wagtail.core import blocks
from wagtail.core.blocks.field_block import URLBlock, CharBlock, IntegerBlock

class DocumentViewerBlock(blocks.StructBlock):
    url = CharBlock()
    page = IntegerBlock(required=False)

    class Meta:
        template = 'blocks/document.html'
        icon = 'doc-full'