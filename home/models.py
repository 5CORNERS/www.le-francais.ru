from __future__ import absolute_import, unicode_literals

from django.db.models import CharField, SmallIntegerField, OneToOneField, BooleanField, SET_NULL, ForeignKey, URLField, Model
from django.db.models.fields import TextField
from django.forms import CheckboxInput
from modelcluster.fields import ParentalKey
from pybb.models import Topic, Forum, Category
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel, FieldPanel, MultiFieldPanel, PageChooserPanel, \
    InlinePanel
from wagtail.wagtailcore.blocks import RichTextBlock, RawHTMLBlock, ListBlock, StructBlock
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsnippets.models import register_snippet

from home.blocks.AudioBlock import AudioBlock
from home.blocks.DocumentViewerBlock import DocumentViewerBlock
from home.blocks.ForumBlocks import PostBlock
from home.blocks.TabsBlock import TabsBlock, TabBlock
from home.blocks.VideoPlayer import VideoPlayerBlock
from home.blocks.Reviews import ChoosenReviews
# from home.blocks.AdvertismentBlocks import AdvertisementInline


def is_nav_root(page: Page) -> bool:
    if isinstance(page, PageWithSidebar) and page.is_nav_root:
        return True
    if isinstance(page, LessonPage) and page.is_nav_root:
        return True
    else:
        return False


def get_nav_root(page: Page) -> Page:
    current_page = page
    while not is_nav_root(current_page):
        if current_page.get_parent() is None:
            break
        current_page = current_page.get_parent().specific
    return current_page


class IndexPage(Page):
    is_selectable = BooleanField(default=True)
    content_panels = Page.content_panels + [
        InlinePanel('related_pages', label="Related pages"),
        InlinePanel('reviews', label="Reviews"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel('is_selectable')
    ]


class IndexPageReferences(Orderable):
    page = ParentalKey(IndexPage, related_name='related_pages')
    referenced_page = ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+',
    )
    panels = [
        PageChooserPanel('referenced_page'),
    ]


class IndexReviews(Orderable):
    page = ParentalKey(IndexPage, related_name='reviews')
    url = URLField(null=True, blank=True)
    text = CharField(null=True, blank=True, max_length=1024)
    external = BooleanField(default=False)
    panels = [
        FieldPanel('url'),
        FieldPanel('text', TextField),
        FieldPanel('external')
    ]


class DefaultPage(Page):
    show_in_sitemap = BooleanField(default=True)
    # Used to build a reference on main page
    reference_title = TextField(null=True, blank=True)
    subtitle = TextField(null=True, blank=True)
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
    ])


DefaultPage.content_panels = Page.content_panels + [
    FieldPanel('reference_title'),
    FieldPanel('subtitle'),
    StreamFieldPanel('body'),
]
DefaultPage.promote_panels = DefaultPage.promote_panels + [
    FieldPanel('show_in_sitemap')
]


class PageWithSidebar(Page):
    show_in_sitemap = BooleanField(default=True)
    reference_title = TextField(null=True, blank=True)
    subtitle = TextField(null=True, blank=True)
    menu_title = TextField(blank=True)
    is_nav_root = BooleanField(default=False)
    is_selectable = BooleanField(default=True)
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('tabs', TabsBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")
         ),
        ('post', PostBlock()),
        ('choosen_reviews', ChoosenReviews())
    ])

    def get_nav_root(self) -> Page:
        return get_nav_root(self)


PageWithSidebar.content_panels = Page.content_panels + [
    FieldPanel('reference_title'),
    FieldPanel('subtitle'),
    StreamFieldPanel('body'),
]
PageWithSidebar.promote_panels = PageWithSidebar.promote_panels + [
    FieldPanel('menu_title'),
    FieldPanel('show_in_sitemap')
]
PageWithSidebar.settings_panels = PageWithSidebar.settings_panels + [
    FieldPanel('is_nav_root'),
    FieldPanel('is_selectable'),
]


class LessonPage(Page):
    show_in_sitemap = BooleanField(default=True)
    menu_title = TextField(blank=True)
    is_nav_root = BooleanField(default=False)
    is_selectable = BooleanField(default=True)
    reference_title = TextField(null=True, blank=True)
    subtitle = TextField(null=True, blank=True)
    lesson_number = SmallIntegerField(blank=True, null=True)
    summary = CharField(max_length=100, null=True, blank=True)
    repetition_material = CharField(max_length=100, null=True, blank=True)
    audio_material = CharField(max_length=100, null=True, blank=True)
    comments_for_lesson = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('post', PostBlock())
    ], null=True, blank=True)
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('post', PostBlock()),
        # ('advertisement', AdvertisementInline())
    ])
    dictionary = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")),
        ('post', PostBlock())
    ], null=True, blank=True)
    other_tabs = StreamField([('tab', TabBlock())])

    def get_lesson_number(self):
        return self.slug.split("lecon-", 1)[1]

    has_own_topic = BooleanField(default=False)
    topic = OneToOneField(
        Topic,
        on_delete=SET_NULL,
        null=True,
        blank=True
    )

    def get_nav_root(self) -> Page:
        return get_nav_root(self)


LessonPage.content_panels = Page.content_panels + [
    FieldPanel('reference_title'),
    FieldPanel('subtitle'),
    FieldPanel('audio_material'),
    StreamFieldPanel('comments_for_lesson'),
    StreamFieldPanel('body'),
    StreamFieldPanel('dictionary'),
    FieldPanel('summary'),
    FieldPanel('repetition_material'),
    StreamFieldPanel('other_tabs')
]
LessonPage.promote_panels = LessonPage.promote_panels + [
    FieldPanel('menu_title'),
    FieldPanel('show_in_sitemap')
]
LessonPage.settings_panels = LessonPage.settings_panels + [
    FieldPanel('lesson_number'),
    FieldPanel('is_nav_root'),
    FieldPanel('is_selectable'),
    MultiFieldPanel(
        [
            FieldPanel('has_own_topic', widget=CheckboxInput),
            FieldPanel('topic'),
        ],
        heading='Topic',
        classname='collapsible'
    )
]


class ArticlePage(Page):
    show_in_sitemap = BooleanField(default=True)
    allow_comments = BooleanField('allow comments', default=True)
    menu_title = TextField(blank=True)
    is_nav_root = BooleanField(default=False)
    is_selectable = BooleanField(default=True)
    reference_title = TextField(null=True, blank=True)
    subtitle = TextField(null=True, blank=True)
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
    ])

    def get_absolute_url(self):
        return self.full_url

    def get_nav_root(self) -> Page:
        return get_nav_root(self)


ArticlePage.content_panels = ArticlePage.content_panels + [
    FieldPanel('reference_title'),
    FieldPanel('subtitle'),
    StreamFieldPanel('body'),
]
ArticlePage.promote_panels = ArticlePage.promote_panels + [
    FieldPanel('menu_title')
]
ArticlePage.settings_panels = ArticlePage.settings_panels + [
    FieldPanel('allow_comments'),
    FieldPanel('is_nav_root'),
    FieldPanel('is_selectable'),
]

@register_snippet
class AdvertisementSnippet(Model):
    name = CharField(max_length=100, unique=True)
    header = TextField(max_length=1000, blank=True)
    body = TextField(max_length=1000, blank=True)

    panels= [
        FieldPanel('name'),
        FieldPanel('header', RawHTMLBlock()),
        FieldPanel('body', RawHTMLBlock())
    ]