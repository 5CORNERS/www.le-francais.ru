from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks.field_block import URLBlock

class VideoPlayerBlock(blocks.StructBlock):
    source = URLBlock()
    poster = URLBlock(required=False)

    class Meta:
        template='blocks/video_player.html'
        icon = 'media'