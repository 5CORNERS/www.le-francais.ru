from wagtail.core import blocks
from wagtail.core.blocks.field_block import IntegerBlock


class TopicBlock(blocks.StructBlock):
	topic_id = IntegerBlock()

	class Meta:
		template = 'blocks/topic_block.html'
		icon = 'group'

class PostBlock(blocks.StructBlock):
	post_id = IntegerBlock()

	class Meta:
		template = 'blocks/post_block.html'
		icon = 'group'
