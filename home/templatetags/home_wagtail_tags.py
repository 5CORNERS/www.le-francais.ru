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
	tag_name, image_expr, filter_spec_to_be_formatted, *bits = token.split_contents()

	attrs = {}
	output_var_name = None

	as_context = False  # if True, the next bit to be read is the output variable name
	is_valid = True

	for bit in bits:
		if bit == 'as':
			# token is of the form {% image self.photo max-320x200 as img %}
			as_context = True
		elif as_context:
			if output_var_name is None:
				output_var_name = bit
			else:
				# more than one item exists after 'as' - reject as invalid
				is_valid = False
		else:
			name, value = bit.split('=')
			attrs[name] = parser.compile_filter(
				value)  # setup to resolve context variables as value

	image_expr = parser.compile_filter(image_expr)
	return FormatImageNode(image_expr, filter_spec_to_be_formatted, attrs, output_var_name)
