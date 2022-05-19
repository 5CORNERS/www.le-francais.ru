from wagtail.core.blocks import RawHTMLBlock

class InvisibleRawHTMLBlock(RawHTMLBlock):
    def get_context(self, value, parent_context=None):
        context = super(InvisibleRawHTMLBlock, self).get_context(
            value, parent_context)
        if 'lesson_was_payed_by_user' in context.keys() and context['lesson_was_payed_by_user']:
            pass
        else:
            context['value'] = ''
        return context

    def value_from_form(self, value):
        value = super(InvisibleRawHTMLBlock, self).value_from_form(value)
        return value

    class Meta:
        template='blocks/invisible_raw_html_block.html'


class VisibleRawHTMLBlock(InvisibleRawHTMLBlock):
    def get_context(self, value, parent_context=None):
        context = super(InvisibleRawHTMLBlock, self).get_context(
            value, parent_context)
        if 'lesson_was_payed_by_user' in context.keys() and context['lesson_was_payed_by_user']:
            context['value'] = ''
        return context
