from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.db.models import CharField, SmallIntegerField, OneToOneField, IntegerField, BooleanField, SET_NULL, ForeignKey, URLField, \
    Model
from django.db.models.fields import TextField, DateTimeField
from django.forms import CheckboxInput
from modelcluster.fields import ParentalKey
from pybb.models import Topic, Forum, Category
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel, MultiFieldPanel, PageChooserPanel, \
    InlinePanel
from wagtail.core.blocks import RichTextBlock, RawHTMLBlock, ListBlock, StructBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet

from home.blocks.AudioBlock import AudioBlock
from home.blocks.DocumentViewerBlock import DocumentViewerBlock
from home.blocks.ForumBlocks import PostBlock
from home.blocks.Reviews import ChoosenReviews
from home.blocks.TabsBlock import TabsBlock, TabBlock
from home.blocks.VideoPlayer import VideoPlayerBlock
import datetime
from .utils import message

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
    ('none', 'None')
)
PLACEMENT_CHOICES = (
    ('sidebar', 'Sidebar'),
    ('none', 'None'),
    ('resume_top', 'Resume Top'),
    ('resume_bottom', 'Resume Bottom'),
    ('revision_top', 'Revision Top'),
    ('revision_bottom', 'Revision Bottom'),
)


@register_snippet
class InlineAdvertisementSnippet(Model):
    name = CharField(max_length=100, unique=True)
    # id = CharField(max_length=100, unique=True)
    header = TextField(max_length=10000, blank=True)
    body = TextField(max_length=5000, blank=True)
    body_mobile = TextField(max_length=5000, blank=True)

    panels = [
        FieldPanel('name'),
        # FieldPanel('id'),
        FieldPanel('header'),
        FieldPanel('body'),
        FieldPanel('body_mobile')
    ]

    def __str__(self):
        return self.name


from home.blocks.AdvertisementBlocks import AdvertisementInline

@register_snippet
class PageLayoutAdvertisementSnippet(Model):
    name =  CharField(max_length=100, unique=True, blank=False)
    page_type = CharField(max_length=100, choices=PAGE_CHOICES , default='none')
    placement = CharField(max_length=100, choices=PLACEMENT_CHOICES, default='none')
    code = CharField(max_length=30, blank=True, default='')
    head = StreamField([
        ('html', RawHTMLBlock()),
    ], blank=True)
    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('html', RawHTMLBlock()),
    ], blank=True)
    live = BooleanField(default=True)
    panels = [
        FieldPanel('name'),
        FieldPanel('code'),
        FieldPanel('page_type'),
        FieldPanel('placement'),
        FieldPanel('live'),
        StreamFieldPanel('head'),
        StreamFieldPanel('body'),
    ]

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
    page_type = CharField(max_length=100,choices=PAGE_CHOICES,default='index_page')
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
    page_type = CharField(max_length=100,choices=PAGE_CHOICES,default='none')
    show_in_sitemap = BooleanField(default=True)
    reference_title = TextField(null=True, blank=True)
    subtitle = TextField(null=True, blank=True)
    menu_title = TextField(blank=True)
    is_nav_root = BooleanField(default=False)
    is_selectable = BooleanField(default=True)
    body = StreamField([
        ('advertisement', AdvertisementInline()),
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
    ], blank=True)

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
    FieldPanel('page_type'),
    FieldPanel('is_nav_root'),
    FieldPanel('is_selectable'),
]


class LessonPage(Page):
    page_type = CharField(max_length=100,choices=PAGE_CHOICES,default='none')
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

    need_payment = BooleanField(default=False)

    comments_for_lesson = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('post', PostBlock())
    ], null=True, blank=True)

    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
        ('post', PostBlock()),
    ], blank=True)

    dictionary = StreamField([
        ('advertisement', AdvertisementInline()),
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

    mail_archive = StreamField([
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

    other_tabs = StreamField([('tab', TabBlock())], blank=True)

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

    def __str__(self):
        return "LessonPage "+str(self.lesson_number)

    def add_lesson_to_user(self, user):
        ul = UserLesson(user=user, lesson=self)
        ul.save()
        user.cup_amount -= 1
        user.save()
        return user.cup_amount

    class Meta:
        permissions = (
            ('listen_lesson', 'Can listen lesson'),
        )


LessonPage.content_panels = Page.content_panels + [
    FieldPanel('reference_title'),
    FieldPanel('subtitle'),
    FieldPanel('audio_material'),
    StreamFieldPanel('comments_for_lesson'),
    StreamFieldPanel('body'),
    StreamFieldPanel('dictionary'),
    FieldPanel('summary'),
    FieldPanel('repetition_material'),
    FieldPanel('mail_archive'),
    StreamFieldPanel('other_tabs')
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
    )
]


class ArticlePage(Page):
    page_type = CharField(max_length=100, choices=PAGE_CHOICES, default='article_page')
    show_in_sitemap = BooleanField(default=True)
    allow_comments = BooleanField('allow comments', default=True)
    menu_title = TextField(blank=True)
    is_nav_root = BooleanField(default=False)
    is_selectable = BooleanField(default=True)
    reference_title = TextField(null=True, blank=True)
    subtitle = TextField(null=True, blank=True)
    body = StreamField([
        ('advertisement', AdvertisementInline()),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentViewerBlock()),
        ('html', RawHTMLBlock()),
        ('audio', AudioBlock()),
        ('video', VideoPlayerBlock()),
    ], blank=True)

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
    FieldPanel('page_type')
]

class UserLesson(Model):
    user = ForeignKey('custom_user.User', related_name='payment')
    lesson = ForeignKey('home.LessonPage', related_name='payment')
    date = DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + str(self.lesson)


class Payment(Model):
    cups_amount = IntegerField()
    user = ForeignKey('custom_user.User', related_name='payments')
    datetime_create = DateTimeField(auto_now_add=True)
    datetime_update = DateTimeField(auto_now=True)
    status = IntegerField(default=0)

    e_transaction_total = IntegerField(null=True, default=None)

    e_product_sku = CharField(max_length=20, null=True, default=None)
    e_product_price = IntegerField(null=True, default=None)

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
        return 'Payment '+str(self.id)

    def get_params(self, success_url="https://www.le-francais.ru/payments?success", fail_url="https://www.le-francais.ru/payments?fail"):
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
        currency_id = u'643'  ## Russian rubles
        payment_no = self.id
        description = "www.le-francais.ru -- Покупка " + message(self.cups_amount, 'чашечки', 'чашечек', 'чашечек' ) + " кофе."
        expired_date = self.expired_date().isoformat()
        customer_email = self.user.email
        success_url = success_url + "&payment_amount={0}&payment_id={1}".format(str(payment_amount),str(self.id))

        params = [
            ('WMI_MERCHANT_ID', merchant_id, 'merchant_id'),
            ('WMI_PAYMENT_AMOUNT', payment_amount, 'payment_amount'),
            ('WMI_CURRENCY_ID', currency_id,'currency_id'),
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


class BackUrls(Model):
    success = URLField()
    fail = URLField()
    payment = ForeignKey('tinkoff_merchant.Payment')
