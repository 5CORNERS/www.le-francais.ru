from wagtail.core.blocks import StreamBlock, StructBlock, RichTextBlock, \
	RawHTMLBlock, TextBlock, ChoiceBlock, IntegerBlock, CharBlock, BooleanBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.templatetags.wagtailimages_tags import ImageNode


class FloatingImageBlock(StructBlock):
	image = ImageChooserBlock(required=True)
	image_caption = CharBlock(required=False, help_text='Подпись под картинкой')
	width_large = IntegerBlock(required=True, default=200)
	width_large_as_percentages = BooleanBlock(default=False, required=False)
	width_small = IntegerBlock(required=True, default=200)
	width_small_as_percentages = BooleanBlock(default=False,
	                                         required=False)
	float = ChoiceBlock(choices=[
		('rightimg', 'Float Right'),
		('leftimg', 'Float Left')
	])
	small_image_position = ChoiceBlock(choices=[
		('above', 'Image Above Content'),
		('below', 'Image Below Content')
	], default='above')
	content = StreamBlock(
		[
			('html', RawHTMLBlock()),
			('paragraph', RichTextBlock())
		], required=True
	)
	min_height = BooleanBlock(required=False, default=False)

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
		context['value']['container_height'] = value['image'].height * (value['width_large'] / value['image'].width) + 8 + 5
		if value['image_caption']:
			context['value']['container_height'] += 35
		return context

	class Meta:
		icon='image'
		template='blocks/floating_image.html'
