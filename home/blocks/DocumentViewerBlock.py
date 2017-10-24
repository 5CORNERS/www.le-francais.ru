from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks.field_block import URLBlock

class DocumentViewerBlock(blocks.StructBlock):
    url = URLBlock()

    class Meta:
        template = 'blocks/document.html'
        icon = 'doc-full'