from __future__ import absolute_import, unicode_literals

from django.db import models
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from django.db.models import URLField
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel, MultiFieldPanel, FieldPanel
from wagtail.wagtailcore.blocks import RichTextBlock, RawHTMLBlock, ListBlock, StructBlock, CharBlock
from wagtail.wagtailcore.fields import StreamField

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock

from home.blocks.AudioBlock import AudioBlock
from home.blocks.TabsBlock import TabsBlock, TabBlock


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
        ('tabs', TabsBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")
         )
    ])

PageWithSidebar.content_panels = Page.content_panels + [
    StreamFieldPanel('body'),
]

class LessonPage(Page):
    summary = URLField(null=True, blank=True)
    repetition_material = URLField(null=True, blank=True)
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock())
    ])
    other_tabs = StreamField([('tab', TabBlock())])


LessonPage.content_panels = Page.content_panels + [
    StreamFieldPanel('body'),
    StreamFieldPanel('other_tabs'),
    FieldPanel('summary'),
    FieldPanel('repetition_material')
]
