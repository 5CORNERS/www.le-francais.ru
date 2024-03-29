from datetime import timedelta, datetime
import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, Max
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from tinkoff_merchant.models import Payment as TinkoffPayment, Payment
from tinkoff_merchant.models import ReceiptItem
from tinkoff_merchant.signals import payment_confirm, payment_refund

class CustomUserManager(UserManager):
	def _create_user(self, username, email, password, **extra_fields):
		"""
		Creates and saves a User with the given username, email and password.
		"""
		if not email:
			raise ValueError('Email is required')
		if not username:
			raise ValueError('The given username must be set')
		email = self.normalize_email(email)
		username = self.model.normalize_username(username)
		user = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
	email = models.EmailField(
		verbose_name='email address',
		max_length=255,
		unique=True,
		error_messages={
			'unique': _("A user with that email already exists."),
		},
	)

	name_for_emails = models.CharField(
		max_length=32,
		help_text="Name, which will be used in emails instead of username",
		null=True,
		blank=True,
		default=None,
	)

	username = models.CharField(
		max_length=32,
		verbose_name='nickname',
		help_text='Your forum nickname (can be changed later)',
		unique=True,
		error_messages={
			'unique': _("Пользователь с таким именем уже зарегестрирован."),
		},
	)

	timezone = models.CharField(
		max_length=32,
		verbose_name='timezone',
		null=True
	)

	from django.core.serializers.json import DjangoJSONEncoder
	from django.contrib.postgres.fields import JSONField

	recaptcha3_score = models.FloatField(null=True)

	used_usernames = JSONField(
		encoder=DjangoJSONEncoder, default=list,
		editable=False, verbose_name='Used Usernames')

	push4site = JSONField(
		null=True,
		encoder=DjangoJSONEncoder, default=list,
		verbose_name="push4site ids"
	)

	must_pay = models.BooleanField(
		default=True, editable=True,
		verbose_name='Должен платить',
		help_text='Определяет, должен ли пользователь активировать урок для доступа к материалам')

	saw_message = models.BooleanField(
		default=False, editable=True,
		verbose_name='Видел сообщение',
		help_text='Пользователь получил сообщение о системе активации уроков')
	saw_message_datetime = models.DateTimeField(
		default=None, null=True,
		verbose_name='Дата сообщения')

	show_tickets = models.NullBooleanField(
		null=True
	)

	_cup_amount = models.IntegerField(
		default=0, editable=True,
		verbose_name='Кол-во чашек/билеткиов')
	_cup_credit = models.IntegerField(
		default=0, editable=True,
		verbose_name='Кол-во "кредитных" чашек')

	_low_price = models.BooleanField(
		default=False, editable=True,
		verbose_name='Статус пенсионера/студента')

	country_name = models.CharField(max_length=2000, default=None, null=True, blank=True)
	country_code = models.CharField(max_length=2000, default=None, null=True, blank=True)
	city = models.CharField(max_length=2000, default=None, null=True, blank=True)
	region = models.CharField(max_length=2000, default=None, null=True, blank=True)

	def switch_low_price(self):
		if self._low_price:
			self._low_price = False
		else:
			self._low_price = True
		self.save()
		return self

	def low_price_set_true(self):
		self._low_price = True
		self.save()
		return self

	def low_price_set_false(self):
		self._low_price = False
		self.save()
		return self

	def add_cups(self, n):
		self._cup_amount += n
		self.save()
		return self

	def add_credit_cups(self, n):
		self._cup_credit += n
		self.save()
		return self

	def has_payed(self):
		if self.cup_amount > 0 or self.payed_lessons.all().exists():
			return True
		return False

	@property
	def has_lessons(self) -> bool:
		if self.payed_lessons.all().exists():
			return True
		else:
			return False

	def has_words(self) -> bool:
		if self.flash_cards_data.all().exists():
			return True
		else:
			return False

	@property
	def has_words_or_lessons(self) -> bool:
		if self.has_words or self.has_lessons:
			return True
		else:
			return False

	def last_payment(self):
		try:
			return TinkoffPayment.objects.filter(
				(Q(status='CONFIRMED') | Q(status='AUTHORIZED')) & Q(
					customer_key=self.id)).latest('update_date')
		except TinkoffPayment.DoesNotExist:
			return None

	def days_since_joined(self):
		return (datetime.now(pytz.utc) - self.date_joined).days

	@property
	def cup_amount(self):
		return self._cup_amount

	@property
	def cups_amount(self):
		return self._cup_amount

	@property
	def has_cups(self):
		if self.cups_amount > 0 or self.cup_credit > 0:
			return True
		return False

	@property
	def cup_credit(self):
		return self._cup_credit

	@property
	def low_price(self):
		return self._low_price

	@property
	def latest_lesson_number(self):
		return self.payed_lessons.aggregate(Max('lesson_number'))['lesson_number__max']

	payed_lessons = models.ManyToManyField(
		'home.LessonPage',
		through='home.UserLesson',
		related_name='paid_users')

	def activate_payment(self, payment):
		self.add_cups(payment.cups_amount)
		self.save()

	objects = CustomUserManager()
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	def has_coffee(self):
		if self.cups_amount > 0 or self.cup_credit > 0:
			return True
		else:
			return False

	def __str__(self):
		return self.username

	def email_user(self, subject, message, from_email=None, **kwargs):
		"""
		Sends an email to this User.
		"""
		send_mail(subject, message, from_email, [self.email], **kwargs)

	def nick_name(self):
		return self.username

	def get_username(self):
		return self.username

	def has_active_lessons(self):
		if self.payed_lessons.filter(need_payment=True):
			return True
		return False

	def get_all_payments(self):
		return list(TinkoffPayment.objects.filter(customer_key=self.id))

	def get_user_datetime(self):
		tz = self.timezone
		try:
			return timezone.make_naive(timezone.now(), pytz.timezone(tz))
		except pytz.exceptions.UnknownTimeZoneError:
			return timezone.make_naive(timezone.now(), pytz.utc)

	@property
	def user_datetime(self):
		return self.get_user_datetime()

	def get_pytz_timezone(self):
		try:
			return pytz.timezone(self.timezone)
		except pytz.exceptions.UnknownTimeZoneError:
			return pytz.timezone('UTC')

	@property
	def pytz_timezone(self):
		return self.get_pytz_timezone()

	# Statistics fields in admin interface
	@property
	def recent_login(self):
		session = self.session_set.order_by('-last_activity').first()
		if session:
			last_activity = session.last_activity
		else:
			last_activity = None
		return last_activity

	@property
	def likes_count(self):
		return self.pybb_profile.like_set.all().count()

	@property
	def posts_count(self):
		return self.posts.all().count()

	@property
	def has_orders(self):
		had_orders = Payment.objects.filter(customer_key=self.pk).exists()
		if had_orders:
			return True

	@property
	def payments_amount(self):
		payment_amount = 0
		if self.has_orders:
			for payment in Payment.objects.filter(customer_key=self.pk).filter(
					Q(status='CONFIRMED') | Q(status='AUTHORIZED')):
				payment_amount += payment.amount / 100
		return payment_amount

	@property
	def last_payment_datetime(self):
		last_payment = Payment.objects.order_by('-update_date').filter(
			customer_key=self.pk).filter(Q(status='CONFIRMED') | Q(status='AUTHORIZED')).first()
		if last_payment:
			return last_payment.update_date
		else:
			return None

	def activated_lesson_after_last_payment(self):
		user_lesson = self.payment.select_related('lesson').filter(date__gt=self.last_payment_datetime).order_by(
			'date').first()
		if user_lesson:
			return user_lesson.lesson.lesson_number
		else:
			return None

from django.db import models


class UsedUsernames(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	used_username = models.CharField(max_length=32)
	change_datetime = models.DateTimeField()


class LogMessage(models.Model):
	LISTEN = 1
	DOWNLOAD = 2
	TYPES_CHOICES = [
		(DOWNLOAD, 'Download'),
		(LISTEN, 'listen')
	]
	datetime = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('User', related_name='log_messages', null=True)
	message = models.CharField(max_length=200, null=True)
	value = models.IntegerField(null=True)
	type = models.IntegerField(choices=TYPES_CHOICES, null=True)
	session_key = models.CharField(max_length=40 ,null=True)


@receiver(payment_confirm)
def activate_tinkoff_payment(sender, **kwargs):
	payment = kwargs['payment']
	if payment.customer_key:
		user = User.objects.get(id=int(payment.customer_key))
		quantity = 0
		items = list(payment.receipt.receiptitem_set.all())
		for item in items:
			if item.category in ['coffee_cups', 'tickets']:
				quantity += item.site_quantity
		user.add_cups(quantity)


@receiver(payment_refund)
def deactivate_tinkoff_payment(sender, **kwargs):
	payment = kwargs['payment']
	if payment.customer.key:
		user = User.objects.get(id=int(payment.customer_key))
		quantity = 0
		items = list(payment.receipt.receiptitem_set.all())
		for item in items:
			if item.category in ['coffee_cups', 'tickets']:
				quantity += item.site_quantity
		user.add_cups(-quantity)
