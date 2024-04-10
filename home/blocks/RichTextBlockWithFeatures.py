from __future__ import absolute_import, unicode_literals

from wagtail.core.blocks import RichTextBlock as WagtailRichTextBlock


class RichTextBlock(WagtailRichTextBlock):
    def __init__(self, *args, **kwargs):
        kwargs['features'] = [
            'h1', 'h2', 'h3', 'h4', 'bold', 'italic','ol','ul','hr','link','document-link','image','embed',
            'cm_blue', 'cm_orange', 'cm_red', 'cm_green',
        ]
        super(RichTextBlock, self).__init__(*args, **kwargs)
