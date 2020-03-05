from django import template
from wagtail.images.templatetags.wagtailimages_tags import image, ImageNode

register = template.Library()


class FormatImageNode(ImageNode):
	def render(self, context):
		filter_spec_var = template.Variable(self.filter_spec)
		self.filter_spec = filter_spec_var.resolve(context)
		return super(FormatImageNode, self).render(context)


@register.tag(name="do_image")
def do_image(parser, token):
	try:
		tag_name, image_expr, filter_spec_to_be_formatted = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError(
			"%r tag requires only two argument" % token.contents.split()[0]
		)
	image_expr = parser.compile_filter(image_expr)
	return FormatImageNode(image_expr, filter_spec_to_be_formatted)
