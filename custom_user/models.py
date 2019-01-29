from django.contrib.auth.models import AbstractUser, UserManager
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from tinkoff_merchant.models import Payment as TinkoffPayment
from tinkoff_merchant.signals import payment_confirm, payment_refund
from tinkoff_merchant.models import ReceiptItem

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
	username = models.CharField(
		max_length=32,
		verbose_name='nickname',
		help_text='Your forum nickname (can be changed later)',
		unique=True,
		error_messages={
			'unique': _("Пользователь с таким именем уже зарегестрирован."),
		},
	)

	from django.core.serializers.json import DjangoJSONEncoder
	from django.contrib.postgres.fields import JSONField

	used_usernames = JSONField(encoder=DjangoJSONEncoder, default=list)

	must_pay = models.BooleanField(default=True)

	saw_message = models.BooleanField(default=False)

	_cup_amount = models.IntegerField(default=0)
	_cup_credit = models.IntegerField(default=0)

	_low_price = models.BooleanField(default=False)

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
		if self.has_cups or self.payed_lessons.all().exists():
			return True
		return False

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


	payed_lessons = models.ManyToManyField('home.LessonPage', through='home.UserLesson', related_name='paid_users')

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

	def get_full_name(self):
		return self.username

	def has_active_lessons(self):
		if self.payed_lessons.filter(need_payment=True):
			return True
		return False

	def get_all_payments(self):
		return list(TinkoffPayment.objects.filter(customer_key=self.id))


from django.db import models


class UsedUsernames(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	used_username = models.CharField(max_length=32)
	change_datetime = models.DateTimeField()


@receiver(payment_confirm)
def activate_tinkoff_payment(sender, **kwargs):
	payment = kwargs['payment']
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
	user = User.objects.get(id=int(payment.customer_key))
	quantity = 0
	items = list(payment.receipt.receiptitem_set.all())
	for item in items:
		if item.category in ['coffee_cups', 'tickets']:
			quantity += item.site_quantity
	user.add_cups(-quantity)
