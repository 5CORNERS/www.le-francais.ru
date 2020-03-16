from wagtail.core.blocks import StructBlock, ChoiceBlock, StreamBlock, \
	TextBlock, BooleanBlock, RawHTMLBlock, RichTextBlock
from wagtail.images.blocks import ImageChooserBlock


class BootstrapCalloutBlock(StructBlock):
	color = ChoiceBlock(choices=[
		('bs-callout-primary', 'Primary'),
		('bs-callout-secondary', 'Secondary'),
		('bs-callout-warning', 'Warning'),
		('bs-callout-danger', 'Danger'),
		('bs-callout-success', 'Success'),
		('bs-callout-info', 'Info')
	], required=True)
	heading = TextBlock(required=False)
	heading_color = BooleanBlock(default=True)
	text = StreamBlock([
		('html', RawHTMLBlock()),
		('paragraph', RichTextBlock()),
	])

	class Meta:
		template = 'blocks/bootstrap_callout.html'

