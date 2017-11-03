from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks.field_block import IntegerBlock


class TopicBlock(blocks.StructBlock):
	topic_id = IntegerBlock()

	class Meta:
		template = 'blocks/topic_block'
		icon = 'group'
