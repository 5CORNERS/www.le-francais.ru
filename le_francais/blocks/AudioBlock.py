from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks.field_block import URLBlock


class AudioBlock(blocks.StructBlock):
    url = URLBlock()

    class Meta:
        template = 'blocks/audio_player.html'
        icon = 'media'
