from __future__ import absolute_import, unicode_literals

from django.db.models import CharField
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel, FieldPanel
from wagtail.wagtailcore.blocks import RichTextBlock, RawHTMLBlock, ListBlock, StructBlock
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
    summary = CharField(max_length=100, null=True, blank=True)
    repetition_material = CharField(max_length=100, null=True, blank=True)
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock())
    ])
    other_tabs = StreamField([('tab', TabBlock())])

    def lesson_number(self):
        return self.slug.split("lecon-",1)[1]


LessonPage.content_panels = Page.content_panels + [
    StreamFieldPanel('body'),
    FieldPanel('summary'),
    FieldPanel('repetition_material'),
    StreamFieldPanel('other_tabs')
]