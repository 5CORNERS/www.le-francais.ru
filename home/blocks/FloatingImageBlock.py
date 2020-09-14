from wagtail.core.blocks import StreamBlock, StructBlock, RichTextBlock, \
	RawHTMLBlock, TextBlock, ChoiceBlock, IntegerBlock, CharBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.templatetags.wagtailimages_tags import ImageNode


class FloatingImageBlock(StructBlock):
	image = ImageChooserBlock(required=True)
	image_caption = CharBlock(required=False, help_text='Подпись под картинкой')
	width_large = IntegerBlock(required=True, default=200)
	width_small = IntegerBlock(required=True, default=200)
	float = ChoiceBlock(choices=[
		('rightimg', 'Float Right'),
		('leftimg', 'Float Left')
	])
	content = StreamBlock(
		[
			('html', RawHTMLBlock()),
			('paragraph', RichTextBlock())
		], required=True
	)

	def get_context(self, value, parent_context=None):
		context = super(FloatingImageBlock, self).get_context(value, parent_context=None)
		context['value']['lg_image_attr'] = 'width-' + str(value['width_large'])
		context['value']['sm_image_attr'] = 'width-' + str(value['width_small'])
		context['value']['lg_image'] = ImageNode(
			context['value']['image'],
			context['value']['lg_image_attr'],
			attrs={},
			output_var_name='lg_image'
		)
		context['value']['sm_image'] = ImageNode(
			context['value']['image'],
			context['value']['sm_image_attr'],
			attrs={},
			output_var_name='sm_image'
		)
		return context

	class Meta:
		icon='image'
		template='blocks/floating_image.html'
