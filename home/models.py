from __future__ import absolute_import, unicode_literals

from django.db import models
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore.blocks import RichTextBlock, RawHTMLBlock
from wagtail.wagtailcore.fields import StreamField

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock

from le_francais.blocks.AudioBlock import AudioBlock


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