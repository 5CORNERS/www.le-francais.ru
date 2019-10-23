from wagtail.core import blocks
from wagtail.core.blocks.field_block import CharBlock, IntegerBlock, \
    BooleanBlock


class LearningAppsBlock(blocks.StructBlock):
    app_id = CharBlock()
    number = IntegerBlock()
    show_lesson_number = BooleanBlock()
    title = CharBlock()
    height = IntegerBlock()
    width = IntegerBlock()

    class Meta:
        template = 'blocks/learning_apps_block.html'
