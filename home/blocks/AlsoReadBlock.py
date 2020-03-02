from wagtail.core.blocks import StructBlock, PageChooserBlock, \
	ListBlock, URLBlock, CharBlock, TextBlock
from wagtail.images.blocks import ImageChooserBlock


class AlsoReadBlock(ListBlock):
	def __init__(self):
		super(AlsoReadBlock, self).__init__(ArticleLink)

	class Meta:
		template = 'blocks/article_also_read.html'



class ArticleLink(StructBlock):
	page = PageChooserBlock(required=False)
	image = ImageChooserBlock(required=False)
	title = CharBlock(required=False)
	description = TextBlock(required=False)
	url = URLBlock(required=False)
	image_src = URLBlock(required=False)

	def get_context(self, value, parent_context=None):
		context = super(ArticleLink, self).get_context(value, parent_context=parent_context)
		if value['page']:
			context['title'] = value['page'].title
			if value['page'].specific.reference_title:
				context['title'] = value['page'].specific.reference_title
			context['image_src'] = value['page'].specific.reference_image.file.url
			context['description'] = value['page'].specific.subtitle
			context['url'] = value['page'].url_path
		if value['image']:
			context['image_src'] = value['image'].file.url
		if value['image_src']:
			context['image_src'] = value['image_src']
		if value['title']:
			context['title'] = value['title']
		if value['description']:
			context['description'] = value['description']
		return context

	class Meta:
		template = 'blocks/article_media_link.html'

