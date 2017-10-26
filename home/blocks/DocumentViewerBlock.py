from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks.field_block import URLBlock, CharBlock

class DocumentViewerBlock(blocks.StructBlock):
    url = CharBlock()

    class Meta:
        template = 'blocks/document.html'
        icon = 'doc-full'