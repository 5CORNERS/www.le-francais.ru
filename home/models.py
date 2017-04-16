from __future__ import absolute_import, unicode_literals

from django.db import models
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore.blocks import RichTextBlock, RawHTMLBlock, ListBlock, StructBlock, CharBlock
from wagtail.wagtailcore.fields import StreamField

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock

from home.blocks.AudioBlock import AudioBlock


class DefaultPage(Page):
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock())
    ])


DefaultPage.content_panels = Page.content_panels + [
    StreamFieldPanel('body'),
]


class PageWithSidebar(Page):
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")
         )
    ])

PageWithSidebar.content_panels = Page.content_panels + [
    StreamFieldPanel('body'),
]
