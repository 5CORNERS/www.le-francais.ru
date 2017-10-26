from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks.field_block import URLBlock, CharBlock

class VideoPlayerBlock(blocks.StructBlock):
    source = CharBlock()
    poster = CharBlock(required=False)

    class Meta:
        template='blocks/video_player.html'
        icon = 'media'