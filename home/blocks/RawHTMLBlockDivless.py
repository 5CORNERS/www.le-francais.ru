from wagtail.wagtailcore.blocks import FieldBlock
from django.utils.html import format_html_join
from django import forms
from django.utils import six
from django.utils.safestring import mark_safe


class RawHTMLBlock(FieldBlock):

    def __init__(self, required=True, help_text=None, max_length=None, min_length=None, **kwargs):
        self.field = forms.CharField(
            required=required, help_text=help_text, max_length=max_length, min_length=min_length,
            widget=forms.Textarea)
        super(RawHTMLBlock, self).__init__(**kwargs)

    def get_default(self):
        return mark_safe(self.meta.default or '')

    def to_python(self, value):
        return mark_safe(value)

    def get_prep_value(self, value):
        # explicitly convert to a plain string, just in case we're using some serialisation method
        # that doesn't cope with SafeText values correctly
        return six.text_type(value)

    def value_for_form(self, value):
        # need to explicitly mark as unsafe, or it'll output unescaped HTML in the textarea
        return six.text_type(value)

    def value_from_form(self, value):
        return mark_safe(value)

    def render_basic(self, value, context=None):
        return format_html_join(
            '\n', '<div class="block-{1}">{0}</div>',
            [
                (child.render(context=context), child.block_type)
                for child in value
            ]
        )

    class Meta:
        icon = 'code'