from wagtail.core import blocks
from wagtail.core.blocks.field_block import CharBlock, IntegerBlock, \
    BooleanBlock, RawHTMLBlock


class LearningAppsBlock(blocks.StructBlock):
    app_id = CharBlock(required=True)
    number = IntegerBlock(required=True)
    show_lesson_number = BooleanBlock(default=True)
    title = CharBlock(required=False)
    height = CharBlock(default='500px')
    width = CharBlock(default='100%')

    class Meta:
        template = 'blocks/learning_apps_block.html'
