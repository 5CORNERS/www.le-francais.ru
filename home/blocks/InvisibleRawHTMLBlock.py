from wagtail.core.blocks import RawHTMLBlock

class InvisibleRawHTMLBlock(RawHTMLBlock):
    def get_context(self, value, parent_context=None):
        context = super(InvisibleRawHTMLBlock, self).get_context(
            value, parent_context)
        if 'already_payed' in context.keys() and context['already_payed']:
            pass
        else:
            context['value'] = ''
        return context

    def value_from_form(self, value):
        value = super(InvisibleRawHTMLBlock, self).value_from_form(value)
        return value

    class Meta:
        template='blocks/invisible_raw_html_block.html'
