from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks.field_block import URLBlock, BooleanBlock


class AudioBlock(blocks.StructBlock):
    url = URLBlock()
    downloadable = BooleanBlock(required=False)

    class Meta:
        template = 'blocks/audio_player.html'
        icon = 'media'
