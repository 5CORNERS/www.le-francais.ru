from __future__ import absolute_import, unicode_literals

import datetime

from django.conf import settings
from django.db.models import CharField, SmallIntegerField, OneToOneField, \
	IntegerField, BooleanField, SET_NULL, ForeignKey, URLField, \
	Model
from django.db.models.fields import TextField, DateTimeField
from django.dispatch import receiver
from django.forms import CheckboxInput
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
from wagtail.snippets.models import register_snippet

from custom_user.models import User
from home.blocks.AudioBlock import AudioBlock
from home.blocks.DocumentViewerBlock import DocumentViewerBlock
from home.blocks.ForumBlocks import PostBlock
from home.blocks.Reviews import ChoosenReviews
from home.blocks.TabsBlock import TabsBlock, TabBlock
from home.blocks.VideoPlayer import VideoPlayerBlock
from tinkoff_merchant.signals import payment_confirm, payment_refund
from .pay54 import Pay34API
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
	('in_house_sidebar', 'In-House Sidebar')
)


@register_snippet
class AdUnit(Model):
	name = CharField(max_length=100, unique=True)
	adunit_code = CharField(max_length=100, unique=True)
	adunit_sizes = CharField(max_length=500, default='')

	size_mapping = ForeignKey('Mapping', blank=True, null=True, default=None)

	page_type = CharField(max_length=20, choices=PAGE_CHOICES, null=True, blank=True, default=None)
	placement = CharField(max_length=20, choices=PLACEMENT_CHOICES, null=True, blank=True, default=None)

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
class Mapping(Model):
	name = CharField(max_length=16, unique=True)
	script = TextField(max_length=1000)

	panels = [
		FieldPanel('name'),
		FieldPanel('script')
	]

	def __str__(self):
		return self.name


@register_snippet
class InlineAdvertisementSnippet(Model):
	name = CharField(max_length=100, unique=True)
	adunit_code = CharField(max_length=100, default='', blank=True, null=True)
	adunit_sizes = CharField(max_length=500, default='', blank=True, null=True)
	header = TextField(max_length=10000, blank=True)
	body = TextField(max_length=5000, blank=True)
	body_mobile = TextField(max_length=5000, blank=True)

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
class PageLayoutAdvertisementSnippet(Model):
	name = CharField(max_length=100, unique=True, blank=False)
	page_type = CharField(max_length=100, choices=PAGE_CHOICES, default='none')
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
	page_type = CharField(max_length=100, choices=PAGE_CHOICES, default='index_page')
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
	page_type = CharField(max_length=100, choices=PAGE_CHOICES, default='none')
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

	without_right_sightbar = BooleanField(default=False)

	def get_template(self, request, *args, **kwargs):
		if self.without_right_sightbar:
			return 'home/page_with_sidebar_without_right_sidebar.html'
		return 'home/page_with_sidebar.html'


PageWithSidebar.content_panels = Page.content_panels + [
	FieldPanel('without_right_sightbar'),
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
	page_type = CharField(max_length=100, choices=PAGE_CHOICES, default='none')
	show_in_sitemap = BooleanField(default=True)
	menu_title = TextField(blank=True)
	is_nav_root = BooleanField(default=False)
	is_selectable = BooleanField(default=True)
	reference_title = TextField(null=True, blank=True)
	subtitle = TextField(null=True, blank=True)
	lesson_number = SmallIntegerField(blank=True, null=True)
	summary = CharField(max_length=100, null=True, blank=True)
	repetition_material = CharField(max_length=100, null=True, blank=True, verbose_name='Révision')
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

	exercise = StreamField([
		('paragraph', RichTextBlock()),
		('html', RawHTMLBlock()),
	], verbose_name='Домашка', null=True, blank=True)

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
		return user.cup_amount

	def payed(self, user: User):
		if self in user.payed_lessons.all():
			return True
		return False

	def must_pay(self, user: User):
		if user.must_pay and self.need_payment:
			return True
		return False

	def get_context(self, request, *args, **kwargs):
		context = super().get_context(request)

		if request.user.is_authenticated and (request.user.has_cups or request.user.payed_lessons.all()):
			context['already_payed'] = True

		if request.user.is_authenticated and self in request.user.payed_lessons.all():
			context['lesson_was_payed_by_user'] = True

		return context

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
	StreamFieldPanel('mail_archive'),
	StreamFieldPanel('exercise'),
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
	without_sightbar = BooleanField(default=False)

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


from django.db.models import PROTECT


class UserLesson(Model):
	user = ForeignKey('custom_user.User', related_name='payment', on_delete=PROTECT)
	lesson = ForeignKey('home.LessonPage', related_name='payment', on_delete=PROTECT)
	date = DateTimeField(auto_now_add=True)
	remains = IntegerField(blank=True, null=True, default=None)

	def __str__(self):
		return '{0} {1} {2}'.format(self.user, self.lesson.lesson_number, self.remains)

	def fill_remains(self):
		self.remains = self.user.cup_amount
		self.save()


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
		return 'Payment ' + str(self.id)

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
		currency_id = u'643'  # Russian rubles
		payment_no = self.id
		description = "www.le-francais.ru -- Покупка " + message(self.cups_amount, 'чашечки', 'чашечек', 'чашечек') + " кофе."
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


class BackUrls(Model):
	success = URLField()
	fail = URLField()
	payment = ForeignKey('tinkoff_merchant.Payment')


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
