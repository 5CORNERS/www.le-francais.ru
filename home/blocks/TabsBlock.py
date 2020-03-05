from wagtail.core import blocks
from wagtail.core.blocks.field_block import RichTextBlock, RawHTMLBlock, CharBlock, BooleanBlock
from wagtail.core.blocks.stream_block import StreamBlock
from wagtail.images.blocks import ImageChooserBlock

from home.blocks.AudioBlock import AudioBlock
from home.blocks.CollapseBlock import CollapseBlock
from home.blocks.DocumentViewerBlock import DocumentViewerBlock
from home.blocks.FloatingImageBlock import FloatingImageBlock
from home.blocks.VideoPlayer import VideoPlayerBlock
from home.blocks.ForumBlocks import TopicBlock, PostBlock


class TabsBlock(blocks.ListBlock):
    def __init__(self):
        super(TabsBlock, self).__init__(TabBlock)

    class Meta:
        template = 'blocks/tabs.html'


class TabBlock(blocks.StructBlock):
    invisible_for_all = BooleanBlock(required=False, help_text='Табик виден только для администраторов, приоритет над всеми')
    visible_only_if_payed = BooleanBlock(required=False, help_text='Табик виден только для пользователей, которые активировали урок')
    title = CharBlock(required=True)
    href = CharBlock(required=True)
    body = StreamBlock([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('topic', TopicBlock()),
        ('post', PostBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
    ])

    # class Meta:
    #     template = 'blocks/audio_player.html'
