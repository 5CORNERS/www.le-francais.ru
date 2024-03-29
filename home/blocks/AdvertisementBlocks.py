from wagtail.core.blocks import StructBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.core.blocks import BooleanBlock

from home.models import InlineAdvertisementSnippet
from home.utils import is_gpt_disabled


class AdvertisementInline(StructBlock):
    advertisement = SnippetChooserBlock(InlineAdvertisementSnippet)
    disable = BooleanBlock(required=False)

    def get_context(self, value, parent_context=None):
        context = super(AdvertisementInline, self).get_context(value, parent_context)
        if parent_context is not None:
            context['gpt_disabled'] = is_gpt_disabled(parent_context['request'])
            context['utm_source'] = f"inline-block:{parent_context['request'].path}"
        else:
            context['gpt_disabled'] = False
            context['utm_source'] = None
        return context

    class Meta:
        icon = 'snippet'
        label = 'Advert'
        template = 'blocks/advertisement_inline.html'


