import uuid
from typing import List
from decimal import *

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .consts import TAXES, TAXATIONS, CATEGORIES, LESSON_TICKETS, \
	COFFEE_CUPS, CATEGORIES_E_NAME, \
	CATEGORIES_E_SKU_PREFIX, PAYMENT_STATUS_CHOICES, \
	PAYMENT_STATUS_AUTHORIZED, PAYMENT_STATUS_CONFIRMED, \
	PAYMENT_PAYED_STATUSES, PAYMENT_STATUS_NEW
from .settings import get_config
from django.contrib.postgres.fields import JSONField

from .utils import Encoder


class Payment(models.Model):
	RESPONSE_FIELDS = {
		'Success': 'success',
		'Status': 'status',
		'PaymentId': 'payment_id',
		'ErrorCode': 'error_code',
		'PaymentURL': 'payment_url',
		'Message': 'message',
		'Details': 'details',
		'RebillId': 'rebill_id'
	}
	amount = models.IntegerField(verbose_name='Сумма в копейках', editable=False)
	order_id = models.CharField(verbose_name='Номер заказа', max_length=100, unique=True, editable=False, blank=True, null=True)
	description = models.TextField(verbose_name='Описание', max_length=250, blank=True, default='', editable=False)

	success = models.BooleanField(verbose_name='Без ошибок', default=False, editable=False)
	status = models.CharField(verbose_name='Статус транзакции', max_length=20, default='', editable=False, choices=PAYMENT_STATUS_CHOICES)
	payment_id = models.CharField(
		verbose_name='Номер транзакции', max_length=20, default='', editable=False)
	error_code = models.CharField(verbose_name='Код ошибки', max_length=20, default='', editable=False)
	payment_url = models.CharField(
		verbose_name='Ссылка на страницу оплаты.',
		help_text='Ссылка на страницу оплаты. По умолчанию ссылка доступна в течение 24 часов.',
		max_length=100, blank=True, default='', editable=False)
	message = models.TextField(verbose_name='Краткое описание ошибки', blank=True, default='', editable=False)
	details = models.TextField(verbose_name='Подробное описание ошибки', blank=True, default='', editable=False)
	customer_key = models.CharField(verbose_name='Идентификатор покупателя', max_length=36, null=True, default=None, editable=False)
	recurrent = models.BooleanField(verbose_name='Идентификатор родительского платежа', default=False)
	rebill_id = models.CharField(verbose_name='Идентификатор автоплатежа', null=True, default=None, max_length=20)

	creation_date = models.DateTimeField(verbose_name='Дата создания заказа', auto_now_add=True, null=True)
	update_date = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True, null=True)
	redirect_due_date = models.DateTimeField(
		verbose_name='Срок жизни ссылки', blank=True, null=True, default=None
	)
	status_history = JSONField(default=list, encoder=Encoder)
	response_history = JSONField(default=list, encoder=Encoder)
	request_history = JSONField(default=list, encoder=Encoder)

	parent = models.ForeignKey('self', on_delete=models.SET_NULL,
	                           default=None, blank=True, null=True,
	                           related_name='children',
	                           related_query_name='child')

	_user = models.ForeignKey('custom_user.User', on_delete=models.SET_NULL, default=None, blank=True, null=True, related_name='tinkoff_payments', related_query_name='tinkoff_payment')

	class Meta:
		verbose_name = 'Заказ'
		verbose_name_plural = 'Заказы'
		ordering = ['-creation_date']

	def __str__(self):
		return 'Заказ #{self.id}:{self.order_id}:{self.payment_id}'.format(self=self)

	def get_email(self):
		if self.user is not None:
			return self.user.email
		if self.receipt:
			return self.receipt.email
		return None

	@property
	def email(self):
		return self.get_email()

	def get_user(self):
		if self._user:
			return self._user
		elif self.customer_key:
			return get_user_model().objects.get(pk=int(self.customer_key))
		return None

	@property
	def username(self):
		if self.user is not None:
			return self.user.username
		else:
			return None

	@property
	def user(self):
		return self.get_user()

	def can_redirect(self) -> bool:
		if self.redirect_due_date and self.redirect_due_date > timezone.now():
			return self.status == PAYMENT_STATUS_NEW and self.payment_url

	def get_or_create_redirect(self):
		try:
			return self.redirect_to_payment_url, False
		except RedirectToPaymentUrl.DoesNotExist:
			return RedirectToPaymentUrl.objects.get_or_create(
				payment=self
			)

	def get_redirect_url(self) -> str:
		redirect2payment, created = self.get_or_create_redirect()
		return redirect2payment.get_url()

	def is_paid(self) -> bool:
		return self.status in PAYMENT_PAYED_STATUSES

	def with_receipt(self, email: str, phone: str = '') -> 'Payment':
		if not self.id:
			self.save()

		if hasattr(self, 'receipt'):
			return self

		Receipt.objects.create(payment=self, email=email, phone=phone)

		return self

	def with_items(self, items: List[dict]) -> 'Payment':
		for item in items:
			ReceiptItem.objects.create(**item, receipt=self.receipt)
		return self

	def to_json(self, data=None) -> dict:
		redirect_due_date_str = self.redirect_due_date.strftime(
				'%Y-%m-%dT%H:%M:%S'
			) + self.redirect_due_date.strftime('%z')[:3] + ':' + self.redirect_due_date.strftime('%z')[3:]
		json = {
			'Amount': self.amount,
			'OrderId': self.order_id,
			'Description': self.description,
			'RedirectDueDate': redirect_due_date_str
		}
		if self.customer_key:
			json['CustomerKey'] = self.customer_key
		if self.recurrent:
			json['Recurrent'] = 'Y'
		if data:
			json['DATA'] = data

		if hasattr(self, 'receipt'):
			json['Receipt'] = self.receipt.to_json()

		return json

	def items(self) -> list:
		return [item for item in self.receipt.receiptitem_set.all()]

	@property
	def closest_activation(self):
		from home.models import UserLesson
		if self.customer_key:
			closest_activation = UserLesson.objects.filter(user_id=int(self.customer_key), date__gt=self.update_date).select_related('lesson').order_by('date').first()
			if closest_activation:
				return closest_activation.lesson.lesson_number
		return '-'

	@property
	def children(self):
		if self.recurrent:
			return list(Payment.objects.filter(parent=self))

	@property
	def visited_through_redirect(self) -> bool:
		return self.redirect_to_payment_url.visited is not None


class Receipt(models.Model):
	payment = models.OneToOneField(to=Payment, on_delete=models.CASCADE, verbose_name='Заказ')
	email = models.CharField(
		verbose_name='Электронный адрес для отправки чека покупателю', max_length=64)
	phone = models.CharField(verbose_name='Телефон покупателя', max_length=64, blank=True, default='')
	taxation = models.CharField(verbose_name='Система налогообложения', choices=TAXATIONS, max_length=20)

	class Meta:
		verbose_name = 'Данные чека'
		verbose_name_plural = 'Данные чеков'

	def __str__(self):
		return '{self.id} ({self.payment})'.format(self=self)

	def save(self, *args, **kwargs):
		if not self.taxation:
			self.taxation = get_config()['TAXATION']

		return super().save(*args, **kwargs)

	def to_json(self) -> dict:
		result = {}
		if self.email:
			result['Email'] = self.email
		elif self.phone:
			result['Phone'] = self.phone
		result['Taxation'] = self.taxation
		result['Items'] = [item.to_json() for item in self.receiptitem_set.all()]
		return result

	def to_json_pay54(self, receipt_type: int, tax_type: int) -> dict:
		return {
			'type': receipt_type,
			'uniqueId': self.id,
			'customerPhone': self.phone,
			'customerEmail': self.email,
			'positions': [item.to_json_pay54(tax_type) for item in self.receiptitem_set.all()]
		}


class ReceiptItem(models.Model):
	receipt = models.ForeignKey(to=Receipt, on_delete=models.CASCADE, verbose_name='Чек')
	name = models.CharField(verbose_name='Наименование товара', max_length=128)
	price = models.IntegerField(verbose_name='Цена в копейках')
	quantity = models.DecimalField(verbose_name='Количество/вес', max_digits=20, decimal_places=3)
	amount = models.IntegerField(verbose_name='Сумма в копейках')
	tax = models.CharField(verbose_name='Ставка налога', max_length=10, choices=TAXES)
	ean13 = models.CharField(verbose_name='Штрих-код', max_length=20, blank=True, default='')
	shop_code = models.CharField(verbose_name='Код магазина', max_length=64, blank=True, default='')

	category = models.CharField(verbose_name='Категория товара', choices=CATEGORIES, default='', max_length=20)
	site_quantity = models.IntegerField(null=True)

	class Meta:
		verbose_name = 'Информация о товаре'
		verbose_name_plural = 'Информация о товарах'

	def __str__(self):
		return '{self.id} (Чек {self.receipt.id})'.format(self=self)

	def save(self, *args, **kwargs):
		if not self.amount:
			self.amount = self.price * self.quantity
		if not self.tax:
			self.tax = get_config()['ITEM_TAX']
		return super().save(*args, **kwargs)

	def to_json(self) -> dict:
		return {
			'Name': self.name,
			'Price': self.price,
			'Quantity': self.quantity,
			'Amount': self.amount,
			'Tax': self.tax,
			'Ean13': self.ean13,
			'ShopCode': self.shop_code,
		}

	def to_json_pay54(self, tax: int) -> dict:
		return {
			'name': self.name,
			'price': self.price/100,
			'count': self.quantity,
			'tax': tax,
		}

	def e_sku(self):
		return '{0}{1}'.format(CATEGORIES_E_SKU_PREFIX[self.category], self.site_quantity if self.site_quantity else '')

	def e_name(self):
		return '{0}{1}'.format(CATEGORIES_E_NAME[self.category],f' {self.site_quantity}' if self.site_quantity else '')

class RedirectToPaymentUrl(models.Model):
	payment = models.OneToOneField(Payment, related_name='redirect_to_payment_url',
	                               unique=True, on_delete=models.CASCADE)
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	visited = models.DateTimeField(null=True, blank=True)

	def get_url(self):
		return reverse('tinkoff_payment:redirect_to_payment', kwargs={'uuid': self.uuid})
