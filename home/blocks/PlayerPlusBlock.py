import shortuuid
from wagtail.core import blocks
import string, random


class SpeakerHTMLBlock(blocks.StructBlock):
    html = blocks.RawHTMLBlock()
    color_before = blocks.CharBlock(default='#212529')
    color_after = blocks.CharBlock(default='#212529')
    opacity_before = blocks.IntegerBlock(default=0)
    opacity_after = blocks.IntegerBlock(default=100)

class PlayerPlusBlock(blocks.StructBlock):
    audio_url = blocks.URLBlock()
    speakers = blocks.ListBlock(SpeakerHTMLBlock)
    map = blocks.RawHTMLBlock()

    def get_context(self, value, parent_context=None):
        context = super(PlayerPlusBlock, self).get_context(value,
                                                      parent_context=None)
        uuid = shortuuid.uuid()
        context['id'] = uuid
        return context

    class Meta:
        template = 'blocks/player_plus.html'
