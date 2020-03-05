from django.utils.crypto import get_random_string
from wagtail.core.blocks import StreamBlock, StructBlock, TextBlock, RawHTMLBlock, RichTextBlock
from wagtail.images.blocks import ImageChooserBlock

from home.blocks.FloatingImageBlock import FloatingImageBlock


class NestedCollapseBlock(StructBlock):
	heading = TextBlock(required=True)
	content = StreamBlock([
		('text', TextBlock()),
		('html', RawHTMLBlock()),
		('paragraph', RichTextBlock()),
		('image', ImageChooserBlock()),
		('floating_image', FloatingImageBlock()),
	], required=True)

	def get_context(self, value, parent_context=None):
		context = super(NestedCollapseBlock, self).get_context(value, parent_context)
		context['id'] = get_random_string(length=8)
		return context

	class Meta:
		template='blocks/collapse.html'

class CollapseBlock(NestedCollapseBlock):
	content = StreamBlock([
		('text', TextBlock()),
		('html', RawHTMLBlock()),
		('paragraph', RichTextBlock()),
		('image', ImageChooserBlock()),
		('floating_image', FloatingImageBlock()),
		# ('nested_collapse', NestedCollapseBlock()), TODO: Nested block doesn't work
	], required=True)
