from __future__ import absolute_import, unicode_literals

import datetime
import re
from io import StringIO, BytesIO

from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.db.models import Count, Sum
from django.dispatch import receiver
from django.forms import CheckboxInput, TextInput
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.utils import timezone
from modelcluster.fields import ParentalKey
from pybb.models import Topic, Forum, Category
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel, \
    MultiFieldPanel, PageChooserPanel, \
    InlinePanel
from wagtail.core.blocks import RichTextBlock, RawHTMLBlock, ListBlock, \
    StructBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from custom_user.models import User
from home.blocks.LearningAppsBlock import LearningAppsBlock
from home.blocks.AudioBlock import AudioBlock
from home.blocks.DocumentViewerBlock import DocumentViewerBlock
from home.blocks.ForumBlocks import PostBlock
from home.blocks.Reviews import ChoosenReviews
from home.blocks.TabsBlock import TabsBlock, TabBlock
from home.blocks.VideoPlayer import VideoPlayerBlock
from home.blocks.AlsoReadBlock import AlsoReadBlock
from tinkoff_merchant.signals import payment_confirm, payment_refund
from .blocks.BootstrapCalloutBlock import BootstrapCalloutBlock
from .blocks.CollapseBlock import CollapseBlock
from .blocks.FloatingImageBlock import FloatingImageBlock
from .blocks.InvisibleRawHTMLBlock import InvisibleRawHTMLBlock, VisibleRawHTMLBlock
from .blocks.LeFrancaisAdUnit import LeFrancaisAdUnitBlock, \
    AdUnitSizeBlock, AdUnitSizeBlockAdvanced
from .blocks.PlayerPlusBlock import PlayerPlusBlock
from .pay54 import Pay34API
from .utils import message, parse_tab_delimited_srt_file, sub_html, create_document_from_transcript_srt, \
    get_html_and_map_from_docx

PAGE_CHOICES = (
    ('lesson_a1', 'Lesson A1'),
    ('lesson_a2', 'Lesson A2'),
    ('lesson_b2', 'Lesson_B2'),
    ('lesson_page', 'Lesson Page'),
    ('page_with_sidebar', '\"Page with sidebar\"'),
    ('article_page', 'Article Page'),
    ('index_page', 'Title Page'),
    ('conjugation_index', 'Conjugation Title'),
    ('conjugation_verb', 'Conjugation Verb'),
    ('podcast_page', 'Podcast Page'),
    ('none', 'None')
)
PLACEMENT_CHOICES = (
    ('sidebar', 'Sidebar'),
    ('none', 'None'),
    ('resume_top', 'Resume Top'),
    ('resume_bottom', 'Resume Bottom'),
    ('revision_top', 'Revision Top'),
    ('revision_bottom', 'Revision Bottom'),
    ('in_house_sidebar', 'In-House Sidebar')
)

BLOCK_RESUME_POPULAIRE_AFTER = 7
BLOCK_REPETITION_MATERIAL_AFTER = 8
BLOCK_EXERCISE_AFTER = 9
BLOCK_FLASHCARDS_AFTER = 10
STRICT_PLAYER_AFTER = 12
FORBID_BACKGROUND_LISTENING_AFTER = 18

def save_visited_pages_history(request, page):
    if page.set_was_on_page_cookie:
        was_on_pages = request.session.get('was_on_pages', {})
        if not isinstance(was_on_pages, dict):
            was_on_pages = {}
        if not page.slug in was_on_pages:
            was_on_pages[page.slug] = {
                'first_time': timezone.now().isoformat(),
                'last_time': None,
                'count': 1
            }
        else:
            was_on_pages[page.slug][
                'last_time'] = timezone.now().isoformat()
            was_on_pages[page.slug]['count'] += 1
        request.session['was_on_pages'] = was_on_pages


@register_snippet
class AdUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    adunit_code = models.CharField(max_length=100, unique=True)
    adunit_sizes = models.CharField(max_length=500, default='')

    size_mapping = models.ForeignKey('Mapping', blank=True, null=True, default=None, on_delete=models.SET_NULL)

    page_type = models.CharField(max_length=20, choices=PAGE_CHOICES, null=True, blank=True, default=None)
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES, null=True, blank=True, default=None)

    panels = [
        FieldPanel('name'),
        FieldPanel('adunit_code'),
        FieldPanel('adunit_sizes'),
        FieldPanel('size_mapping'),
        FieldPanel('page_type'),
        FieldPanel('placement'),
    ]

    def __str__(self):
        return self.name


@register_snippet
class Mapping(models.Model):
    name = models.CharField(max_length=16, unique=True)
    script = models.fields.TextField(max_length=1000)

    sizes = StreamField([
        ('sizes', AdUnitSizeBlockAdvanced())
    ], blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('script'),
        StreamFieldPanel('sizes')
    ]
    @property
    def sizes_json(self):
        if not self.sizes:
            return None
        result = []
        for size in self.sizes:
            part_1 = []
            if size.value['type']:
                part_1.append(size.value['type'])
            else:
                part_1.append('v')
            part_1.append(size.value['window_or_container_size'].split('x'))
            part_2 = []
            for simple_size in size.value['sizes']:
                part_2.append([simple_size['width'], simple_size['height'], simple_size['width_percents']])
            result.append([part_1, part_2])
        return result

    def __str__(self):
        return self.name


@register_snippet
class InlineAdvertisementSnippet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    adunit_code = models.CharField(max_length=100, default='', blank=True, null=True)
    adunit_sizes = models.CharField(max_length=500, default='', blank=True, null=True)
    header = models.fields.TextField(max_length=10000, blank=True)
    body = models.fields.TextField(max_length=5000, blank=True)
    body_mobile = models.fields.TextField(max_length=5000, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('adunit_code'),
        FieldPanel('adunit_sizes'),
        FieldPanel('header'),
        FieldPanel('body'),
        FieldPanel('body_mobile')
    ]

    def __str__(self):
        return self.name

    def get_sizes(self):
        return self.adunit_sizes


from home.blocks.AdvertisementBlocks import AdvertisementInline


@register_snippet
class PageLayoutAdvertisementSnippet(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    page_type = models.CharField(max_length=100, choices=PAGE_CHOICES, default='none')
    placement = models.CharField(max_length=100, choices=PLACEMENT_CHOICES, default='none')
    code = models.CharField(max_length=30, blank=True, default='')
    head = StreamField([
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
    ], blank=True)
    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
    ], blank=True)
    live = models.BooleanField(default=True)
    panels = [
        FieldPanel('name'),
        FieldPanel('code'),
        FieldPanel('page_type'),
        FieldPanel('placement'),
        FieldPanel('live'),
        FieldPanel('sizes'),
        StreamFieldPanel('head'),
        StreamFieldPanel('body'),
    ]
    sizes = JSONField(default=list, blank=True)

    def get_sizes(self):
        import json
        result = []
        for ad_id in self.get_ad_ids():
            pattern = re.compile(f"(\[.+]),\s?'div-gpt-ad-{ad_id[1]}-{ad_id[2]}'")
            match = re.search(pattern, str(self.head))
            if bool(match) and match.group(1)[0]=='[':
                result.append((f'{ad_id[1]}-{ad_id[2]}', json.loads(match.group(1))))
            else:
                result.append((f'{ad_id[1]}-{ad_id[2]}', None))
        return result



    def get_ad_ids(self):
        return re.finditer(r"display\('div-gpt-ad-(\d{13})-(\d)'\)", str(self.body))

    def __str__(self):
        return self.name


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
    page_type = models.CharField(max_length=100, choices=PAGE_CHOICES, default='index_page')
    is_selectable = models.BooleanField(default=True)
    content_panels = Page.content_panels + [
        InlinePanel('related_pages', label="Related pages"),
        InlinePanel('reviews', label="Reviews"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel('is_selectable')
    ]


class IndexPageReferences(Orderable):
    page = ParentalKey(IndexPage, related_name='related_pages')
    referenced_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    panels = [
        PageChooserPanel('referenced_page'),
    ]


class IndexReviews(Orderable):
    page = ParentalKey(IndexPage, related_name='reviews')
    url = models.URLField(null=True, blank=True)
    text = models.CharField(null=True, blank=True, max_length=1024)
    external = models.BooleanField(default=False)
    show_in_sidebar = models.BooleanField(default=True)
    panels = [
        FieldPanel('url'),
        FieldPanel('text', models.fields.TextField),
        FieldPanel('external', help_text='Will open in new tab'),
        FieldPanel('show_in_sidebar')
    ]

    @property
    def word_count(self):
        return self.text.split(' ').__len__()

    def get_interval(self):
        interval = self.word_count * 60000 // 201
        return interval if interval > 3000 else 3000


class DefaultPage(Page):
    show_in_sitemap = models.BooleanField(default=True)
    # Used to build a reference on main page
    reference_title = models.fields.TextField(null=True, blank=True)
    subtitle = models.fields.TextField(null=True, blank=True)
    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('tabs', TabsBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")
         ),
        ('post', PostBlock()),
        ('choosen_reviews', ChoosenReviews()),
        ('read_also', AlsoReadBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('player_plus', PlayerPlusBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], blank=True)


DefaultPage.content_panels = Page.content_panels + [
    FieldPanel('reference_title'),
    FieldPanel('subtitle'),
    StreamFieldPanel('body'),
]
DefaultPage.promote_panels = DefaultPage.promote_panels + [
    FieldPanel('show_in_sitemap')
]


class PageWithSidebar(Page):
    page_type = models.CharField(max_length=100, choices=PAGE_CHOICES, default='none')
    show_in_sitemap = models.BooleanField(default=True)
    reference_title = models.fields.TextField(null=True, blank=True)
    subtitle = models.fields.TextField(null=True, blank=True)
    menu_title = models.fields.TextField(blank=True)
    is_nav_root = models.BooleanField(default=False)
    is_selectable = models.BooleanField(default=True)
    reference_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('tabs', TabsBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")
         ),
        ('post', PostBlock()),
        ('choosen_reviews', ChoosenReviews()),
        ('read_also', AlsoReadBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('player_plus', PlayerPlusBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], blank=True)

    def get_nav_root(self) -> Page:
        return get_nav_root(self)

    without_right_sightbar = models.BooleanField(default=False)

    set_was_on_page_cookie = models.BooleanField(default=True)

    def serve(self, request, *args, **kwargs):
        save_visited_pages_history(request, self)
        return super(PageWithSidebar, self).serve(request, *args,
                                              **kwargs)

    def get_template(self, request, *args, **kwargs):
        if self.without_right_sightbar:
            return 'home/page_with_sidebar_without_right_sidebar.html'
        return 'home/page_with_sidebar.html'


PageWithSidebar.content_panels = Page.content_panels + [
    FieldPanel('without_right_sightbar'),
    FieldPanel('reference_title'),
    ImageChooserPanel('reference_image'),
    FieldPanel('subtitle'),
    StreamFieldPanel('body'),
]
PageWithSidebar.promote_panels = PageWithSidebar.promote_panels + [
    FieldPanel('menu_title'),
    FieldPanel('show_in_sitemap')
]
PageWithSidebar.settings_panels = PageWithSidebar.settings_panels + [
    FieldPanel('page_type'),
    FieldPanel('is_nav_root'),
    FieldPanel('is_selectable'),
]


class LessonPage(Page):
    page_type = models.CharField(max_length=100, choices=PAGE_CHOICES, default='none')
    show_in_sitemap = models.BooleanField(default=True)
    menu_title = models.fields.TextField(blank=True)
    is_nav_root = models.BooleanField(default=False)
    is_selectable = models.BooleanField(default=True)
    reference_title = models.fields.TextField(null=True, blank=True)
    subtitle = models.fields.TextField(null=True, blank=True)
    lesson_number = models.SmallIntegerField(blank=True, null=True)
    summary = models.CharField(max_length=100, null=True, blank=True)
    repetition_material = models.CharField(max_length=100, null=True, blank=True, verbose_name='Révision')
    audio_material = models.CharField(max_length=100, null=True, blank=True)
    audio_new = models.URLField(blank=True, null=True, default=None)

    need_payment = models.BooleanField(default=False)

    has_transcript = models.BooleanField(default=False)
    transcript = JSONField(default=[], blank=True)
    transcript_html = models.fields.TextField(default='', blank=True)

    transcript_srt = models.FileField(null=True, blank=True, default=None, upload_to='home/transcripts')
    transcript_docx = models.FileField(null=True, blank=True, default=None, upload_to='home/transcripts')
    transcript_text = models.fields.TextField(null=True, blank=True, default=None)

    reference_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body_tab_name = models.CharField(max_length=64, null=True, blank=True)
    previous_lesson_button = models.CharField(max_length=64, null=True, blank=True)
    enable_previous_lesson_button = models.BooleanField(default=True, blank=True)
    next_lesson_button = models.CharField(max_length=64, null=True, blank=True)
    enable_next_lesson_button = models.BooleanField(default=True, blank=True)

    users = models.ManyToManyField(to=User, through='home.UserLesson')

    comments_for_lesson = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('post', PostBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('player_plus', PlayerPlusBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], null=True, blank=True)

    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('post', PostBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('player_plus', PlayerPlusBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], blank=True)

    dictionary_tab_name = models.CharField(max_length=64, blank=True, null=True)

    dictionary = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")),
        ('post', PostBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], null=True, blank=True)

    mail_archive = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")),
        ('post', PostBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], null=True, blank=True)

    exercise = StreamField([
        ('paragraph', RichTextBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('learning_apps', LearningAppsBlock())
    ], verbose_name='Домашка', null=True, blank=True)

    additional_exercise = StreamField([
        ('paragraph', RichTextBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
    ], verbose_name='Exercises De Lecon', null=True, blank=True)
    resume_populaire = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
    ], verbose_name='Народный конспект', null=True, blank=True)
    other_tabs = StreamField([('tab', TabBlock())], blank=True)

    set_was_on_page_cookie = models.BooleanField(default=True)

    def serve(self, request, *args, **kwargs):
        save_visited_pages_history(request, self)
        return super(LessonPage, self).serve(request, *args,
                                              **kwargs)

    @property
    def summary_full_url(self):
        return '//files.le-francais.ru' + self.summary if self.summary else None

    @property
    def repetition_material_full_url(self):
        return '//files.le-francais.ru' + self.repetition_material if self.repetition_material else None

    def get_lesson_number(self):
        return self.slug.split("lecon-", 1)[1]

    has_own_topic = models.BooleanField(default=False)
    topic = models.OneToOneField(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def get_nav_root(self) -> Page:
        return get_nav_root(self)

    def __str__(self):
        return "LessonPage " + str(self.lesson_number)

    def add_lesson_to_user(self, user):
        if user.cup_amount >= 1:
            user.add_cups(-1)
        elif user.cup_credit >= 1:
            user.add_cups(-1)
            user.add_credit_cups(-1)
        else:
            return False
        ul = UserLesson(user=user, lesson=self)
        ul.fill_remains()
        ul.save()

        if self.need_payment and user.must_pay:
            show_tickets = True
        else:
            show_tickets = False
        if user.show_tickets != show_tickets:
            user.show_tickets = show_tickets
            user.save()

        return user.cup_amount

    def flash_cards_is_included(self):
        if self.dictionary_packets.exists():
            return True
        else:
            return False

    def has_verbs(self):
        if self.verbpacket_set.exists():
            return True
        return False

    def several_word_packets(self):
        if self.dictionary_packets.all().count() > 1:
            return True
        else:
            return False

    def get_word_packets(self) -> list:
        return list(self.dictionary_packets.all())

    def get_words_count(self):
        return self.dictionary_packets.annotate(Count('word')).aggregate(Sum('word__count'))['word__count__sum']

    def payed(self, user: User):
        if user.is_authenticated and (self in user.payed_lessons.all() or not user.must_pay):
            return True
        return False

    def must_pay(self, user: User):
        if user.must_pay and self.need_payment:
            return True
        return False

    def serve(self, request: HttpRequest, *args, **kwargs):
        # user = request.user
        # if user.is_authenticated and user.show_tickets != self.must_pay(user):
        # 	user.show_tickets = self.must_pay(user)
        # 	user.save()
        return super(LessonPage, self).serve(request, *args, **kwargs)

    def get_transcript_html_errors_map(self):
        transcript_srt = self.transcript_srt.read().decode('utf-8')
        parsed_srt = parse_tab_delimited_srt_file(StringIO(transcript_srt))
        html = ""
        errors = []
        if self.transcript_text:
            for paragraph in self.transcript_text.split('\n'):
                html += f'<p>{paragraph}</p>'
            html, errors = sub_html(html, parsed_srt)
        else:
            for l, data in parsed_srt.items():
                html += f'<span class="transcript-line" id="{data["id"]}" data-start="{data["start"]}"' \
                        f' data-end="{data["end"]}"' \
                        f' data-speaker="{data["speaker"]}"' \
                        f'>{l}</span>'
        start_ends_map = []
        for d in parsed_srt.values():
            start_ends_map.append({'start': int(d['start']), 'end': int(d['end']), 'id': d['id']})
        return html, errors, start_ends_map

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        user = request.user
        first_need_payment_lesson_number = LessonPage.objects.filter(
            need_payment=True).order_by('lesson_number').first().lesson_number

        context['already_payed'] = False
        if request.user.is_authenticated and (request.user.has_cups or request.user.payed_lessons.all()):
            context['already_payed'] = True

        context['lesson_was_payed_by_user'] = False
        if request.user.is_authenticated and self in request.user.payed_lessons.all():
            context['lesson_was_payed_by_user'] = True
        context['block_exercise'] = True
        if self.exercise:
            if (BLOCK_EXERCISE_AFTER >= self.lesson_number or self.payed(user)):
                context['block_exercise'] = False
        context['block_additional_exercise'] = True
        if self.additional_exercise:
            if (6 >= self.lesson_number or self.payed(user)):
                context['block_additional_exercise'] = False
        context['block_resume_populaire'] = True
        if self.resume_populaire:
            if (BLOCK_RESUME_POPULAIRE_AFTER >= self.lesson_number or self.payed(user)):
                context['block_resume_populaire'] = False
        context['block_repetition_material'] = True
        if self.repetition_material:
            if (BLOCK_REPETITION_MATERIAL_AFTER >= self.lesson_number or self.payed(user)):
                context['block_repetition_material'] = False
        context['block_flash_cards'] = True
        if self.flash_cards_is_included():
            if (BLOCK_FLASHCARDS_AFTER >= self.lesson_number or self.payed(user)):
                context['block_flash_cards'] = False

        context['strict_player'] = True
        if STRICT_PLAYER_AFTER >= self.lesson_number or self.payed(user):
            context['strict_player'] = False

        context['forbid_background'] = True
        if FORBID_BACKGROUND_LISTENING_AFTER >= self.lesson_number or self.payed(user):
            context['forbid_background'] = False

        context['has_transcript'] = False
        if self.transcript_docx.name and self.has_transcript == False:
            self.has_transcript = context['has_transcript'] = True
            self.transcript, self.transcript_html = get_html_and_map_from_docx(BytesIO(self.transcript_docx.read()))
            self.save()
            context['transcript_html'], context['transcript_map'] = self.transcript, self.transcript_html
        elif self.has_transcript:
            context['has_transcript'] = True
            context['transcript_html'], context['transcript_map'] = self.transcript, self.transcript_html

        return context

    def create_transcript_docx(self):
        self.transcript_docx.delete(save=True)
        self.transcript_docx.save(
            f'lesson-{str(self.lesson_number).zfill(3)}.docx',
            create_document_from_transcript_srt(self.transcript_srt.read().decode('utf-8')),
            save=True
        )

    class Meta:
        permissions = (
            ('listen_lesson', 'Can listen lesson'),
        )


LessonPage.content_panels = Page.content_panels + [
    FieldPanel('reference_title'),
    ImageChooserPanel('reference_image'),
    FieldPanel('subtitle'),
    FieldPanel('audio_material'),
    StreamFieldPanel('comments_for_lesson'),
    FieldPanel('body_tab_name'),
    StreamFieldPanel('body'),
    FieldPanel('dictionary_tab_name'),
    StreamFieldPanel('dictionary'),
    FieldPanel('summary'),
    FieldPanel('repetition_material'),
    StreamFieldPanel('mail_archive'),
    StreamFieldPanel('exercise'),
    StreamFieldPanel('additional_exercise'),
    StreamFieldPanel('resume_populaire'),
    StreamFieldPanel('other_tabs'),
]
LessonPage.promote_panels = LessonPage.promote_panels + [
    FieldPanel('menu_title'),
    FieldPanel('show_in_sitemap')
]
LessonPage.settings_panels = LessonPage.settings_panels + [
    FieldPanel('lesson_number'),
    FieldPanel('page_type'),
    FieldPanel('is_nav_root'),
    FieldPanel('is_selectable'),
    MultiFieldPanel(
        [
            FieldPanel('has_own_topic', widget=CheckboxInput),
            FieldPanel('topic'),
        ],
        heading='Topic',
        classname='collapsible'
    ),
    FieldPanel('audio_new'),
    FieldPanel('transcript_srt'),
    FieldPanel('transcript_docx'),
    FieldPanel('enable_previous_lesson_button'),
    FieldPanel('previous_lesson_button', widget=TextInput(attrs={'placeholder':'Предыдущий урок'})),
    FieldPanel('enable_next_lesson_button'),
    FieldPanel('next_lesson_button',  widget=TextInput(attrs={'placeholder':'Следующий урок'})),
]


class ArticlePage(Page):
    page_type = models.CharField(max_length=100, choices=PAGE_CHOICES, default='article_page')
    show_in_sitemap = models.BooleanField(default=True)
    allow_comments = models.BooleanField('allow comments', default=True)
    menu_title = models.fields.TextField(blank=True)
    is_nav_root = models.BooleanField(default=False)
    is_selectable = models.BooleanField(default=True)
    reference_title = models.fields.TextField(null=True, blank=True)
    subtitle = models.fields.TextField(null=True, blank=True)
    reference_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('tabs', TabsBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")
         ),
        ('post', PostBlock()),
        ('choosen_reviews', ChoosenReviews()),
        ('read_also', AlsoReadBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('player_plus', PlayerPlusBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], blank=True)
    without_sightbar = models.BooleanField(default=False)
    set_was_on_page_cookie = models.BooleanField(default=True)

    def serve(self, request, *args, **kwargs):
        save_visited_pages_history(request, self)
        return super(ArticlePage, self).serve(request, *args,
                                              **kwargs)

    def get_absolute_url(self):
        return self.full_url

    def get_nav_root(self) -> Page:
        return get_nav_root(self)

    def get_template(self, request, *args, **kwargs):
        if self.without_sightbar:
            return 'home/article_page_without_sightbar.html'
        return 'home/article_page.html'


ArticlePage.content_panels = ArticlePage.content_panels + [
    FieldPanel('without_sightbar'),
    FieldPanel('reference_title'),
    ImageChooserPanel('reference_image'),
    FieldPanel('subtitle'),
    StreamFieldPanel('body'),
]
ArticlePage.promote_panels = ArticlePage.promote_panels + [
    FieldPanel('menu_title'),
    FieldPanel('show_in_sitemap'),
]
ArticlePage.settings_panels = ArticlePage.settings_panels + [
    FieldPanel('allow_comments'),
    FieldPanel('is_nav_root'),
    FieldPanel('is_selectable'),
    FieldPanel('page_type'),
]


class PodcastPage(Page):
    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('tabs', TabsBlock()),
        ('translations', ListBlock(StructBlock([
            ('word', RichTextBlock(required=True)),
            ('translation', RichTextBlock(required=True))
        ]), template="blocks/transcriptions.html")
         ),
        ('post', PostBlock()),
        ('choosen_reviews', ChoosenReviews()),
        ('read_also', AlsoReadBlock()),
        ('floating_image', FloatingImageBlock()),
        ('collapse', CollapseBlock()),
        ('bootstrap_callout', BootstrapCalloutBlock()),
        ('player_plus', PlayerPlusBlock()),
        ('le_francais_ad_unit', LeFrancaisAdUnitBlock()),
    ], blank=True)
    menu_title = models.fields.TextField(blank=True)
    reference_title = models.fields.TextField(null=True, blank=True)
    subtitle = models.fields.TextField(null=True, blank=True)
    show_in_sitemap = models.BooleanField(default=True)
    reference_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    page_type = models.CharField(max_length=100, choices=PAGE_CHOICES, default='podcast_page')
    set_was_on_page_cookie = models.BooleanField(default=True)

    def serve(self, request, *args, **kwargs):
        save_visited_pages_history(request, self)
        return super(PodcastPage, self).serve(request, *args, **kwargs)

    def get_absolute_url(self):
        return self.full_url

    def get_nav_root(self) -> Page:
        return get_nav_root(self)


PodcastPage.content_panels = PodcastPage.content_panels + [
    FieldPanel('reference_title'),
    ImageChooserPanel('reference_image'),
    FieldPanel('subtitle'),
    StreamFieldPanel('body'),
]
PodcastPage.promote_panels = PodcastPage.promote_panels + [
    FieldPanel('menu_title'),
    FieldPanel('show_in_sitemap'),
]
PodcastPage.settings_panels = PodcastPage.settings_panels + [
    FieldPanel('page_type'),
]


class HTMLPage(Page):
    body = StreamField([('html', RawHTMLBlock()),
        ('visible_html', VisibleRawHTMLBlock()),
        ('invisible_html', InvisibleRawHTMLBlock()), ], blank=True)

    set_was_on_page_cookie = models.BooleanField(default=True)

    def serve(self, request, *args, **kwargs):
        save_visited_pages_history(request, self)
        return super(HTMLPage, self).serve(request, *args, **kwargs)

    def get_template(self, request, *args, **kwargs):
        return 'home/landing_page.html'


HTMLPage.content_panels = HTMLPage.content_panels + [StreamFieldPanel('body')]
HTMLPage.settings_panels = HTMLPage.settings_panels + [FieldPanel('set_was_on_page_cookie')]


class UserLesson(models.Model):
    user = models.ForeignKey('custom_user.User', related_name='payment', on_delete=models.PROTECT)
    lesson = models.ForeignKey('home.LessonPage', related_name='payment', on_delete=models.PROTECT)
    date = models.fields.DateTimeField(auto_now_add=True)
    remains = models.IntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return '{0} {1} {2}'.format(self.user, self.lesson.lesson_number, self.remains)

    def fill_remains(self):
        self.remains = self.user.cup_amount
        self.save()


class Payment(models.Model):
    cups_amount = models.IntegerField()
    user = models.ForeignKey('custom_user.User', related_name='payments', null=True, on_delete=models.SET_NULL)
    datetime_create = models.fields.DateTimeField(auto_now_add=True)
    datetime_update = models.fields.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    e_transaction_total = models.IntegerField(null=True, default=None)

    e_product_sku = models.CharField(max_length=20, null=True, default=None)
    e_product_price = models.IntegerField(null=True, default=None)

    def e_product_name(self):
        return "Coffee Cup"

    def e_product_category(self):
        return "Donation"

    def e_product_quantity(self):
        return self.cups_amount

    def activate_payment(self):
        self.user.activate_payment(self)
        self.status = 1
        self.save()

    def expired_date(self):
        return self.datetime_create + datetime.timedelta(weeks=3)

    def __str__(self):
        return 'Payment ' + str(self.id)

    def get_params(self, success_url="https://www.le-francais.ru/payments?success",
                   fail_url="https://www.le-francais.ru/payments?fail"):
        merchant_id = settings.WALLET_ONE_MERCHANT_ID

        if self.cups_amount == 1:
            payment_amount = 68
            self.e_product_sku = 'C01'
            self.e_product_price = 68
        elif self.cups_amount == 5:
            payment_amount = 295
            self.e_product_sku = 'C05'
            self.e_product_price = 59
        elif self.cups_amount == 10:
            payment_amount = 490
            self.e_product_sku = 'C10'
            self.e_product_price = 49
        elif self.cups_amount == 20:
            payment_amount = 780
            self.e_product_sku = 'C20'
            self.e_product_price = 39
        elif self.cups_amount == 50:
            payment_amount = 1690
            self.e_product_sku = 'C50'
            self.e_product_price = 34

        self.e_transaction_total = payment_amount
        self.save()
        currency_id = u'643'  # Russian rubles
        payment_no = self.id
        description = "www.le-francais.ru -- Покупка " + message(self.cups_amount, 'чашечки', 'чашечек',
                                                                 'чашечек') + " кофе."
        expired_date = self.expired_date().isoformat()
        customer_email = self.user.email
        success_url = success_url + "&payment_amount={0}&payment_id={1}".format(str(payment_amount), str(self.id))

        params = [
            ('WMI_MERCHANT_ID', merchant_id, 'merchant_id'),
            ('WMI_PAYMENT_AMOUNT', payment_amount, 'payment_amount'),
            ('WMI_CURRENCY_ID', currency_id, 'currency_id'),
            ('WMI_PAYMENT_NO', payment_no, 'payment_no'),
            ('WMI_DESCRIPTION', description, 'description'),
            ('WMI_SUCCESS_URL', success_url, 'success_url'),
            ('WMI_FAIL_URL', fail_url, 'fail_url'),
            ('WMI_EXPIRED_DATE', expired_date, 'expired_date'),
            ('WMI_CUSTOMER_EMAIL', customer_email, 'customer_email'),
        ]
        from .utils import get_signature
        signature = get_signature(params).decode('utf-8')
        params.append(('WMI_SIGNATURE', signature, 'signature'))

        return {'params': params}


class BackUrls(models.Model):
    success = models.URLField()
    fail = models.URLField()
    payment = models.ForeignKey('tinkoff_merchant.Payment', on_delete=models.CASCADE)


class WagtailPageNavTree(models.Model):
    page = AutoOneToOneField(Page, on_delete=models.CASCADE, related_name='nav_tree')
    tree = JSONField(default={}, blank=True, null=True)


@receiver(payment_confirm)
def send_receipt(sender, **kwargs):
    if settings.DEBUG:
        return
    pay34_api = Pay34API()
    pay34_api.send_receipt_request(kwargs['payment'])


@receiver(payment_refund)
def send_refund(sender, **kwargs):
    if settings.DEBUG:
        return
    pay34_api = Pay34API()
    pay34_api.send_refund_request(kwargs['payment'])
