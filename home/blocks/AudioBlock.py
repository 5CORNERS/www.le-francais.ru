from wagtail.core import blocks
from wagtail.core.blocks.field_block import URLBlock, BooleanBlock, CharBlock


class AudioBlock(blocks.StructBlock):
    url = CharBlock()
    downloadable = BooleanBlock(required=False)

    class Meta:
        template = 'blocks/audio_player.html'
        icon = 'media'
