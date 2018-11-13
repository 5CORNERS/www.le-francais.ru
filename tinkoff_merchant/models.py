from typing import List
from decimal import *
from django.db import models

from .consts import TAXES, TAXATIONS, CATEGORIES
from .settings import get_config
from django.contrib.postgres.fields import JSONField

class Payment(models.Model):
	RESPONSE_FIELDS = {
		'Success': 'success',
		'Status': 'status',
		'PaymentId': 'payment_id',
		'ErrorCode': 'error_code',
		'PaymentURL': 'payment_url',
		'Message': 'message',
		'Details': 'details',
	}
	amount = models.IntegerField(verbose_name='Сумма в копейках', editable=False)
	order_id = models.CharField(verbose_name='Номер заказа', max_length=100, unique=True, editable=False, blank=True, null=True)
	description = models.TextField(verbose_name='Описание', max_length=250, blank=True, default='', editable=False)

	success = models.BooleanField(verbose_name='Без ошибок', default=False, editable=False)
	status = models.CharField(verbose_name='Статус транзакции', max_length=20, default='', editable=False)
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

	creation_date = models.DateTimeField(verbose_name='Дата создания заказа', auto_now_add=True, null=True)
	update_date = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True, null=True)
	status_history = JSONField(default=list)

	class Meta:
		verbose_name = 'Заказ'
		verbose_name_plural = 'Заказы'

	def __str__(self):
		return 'Заказ #{self.id}:{self.order_id}:{self.payment_id}'.format(self=self)

	def email(self):
		if self.receipt:
			return self.receipt.email

	def can_redirect(self) -> bool:
		return self.status == 'NEW' and self.payment_url

	def is_paid(self) -> bool:
		return self.status == 'CONFIRMED' or self.status == 'AUTHORIZED'

	def with_receipt(self, email: str, taxation: str = None, phone: str = '') -> 'Payment':
		if not self.id:
			self.save()

		if hasattr(self, 'receipt'):
			return self

		Receipt.objects.create(payment=self, email=email, phone=phone, taxation=taxation)

		return self

	def with_items(self, items: List[dict]) -> 'Payment':
		for item in items:
			ReceiptItem.objects.create(**item, receipt=self.receipt)
		return self

	def to_json(self, data=None) -> dict:
		json = {
			'Amount': self.amount,
			'OrderId': self.order_id,
			'Description': self.description,
		}
		# if self.customer_key:
		# 	json['CustomerKey'] = self.customer_key
		if data:
			json['DATA'] = data

		if hasattr(self, 'receipt'):
			json['Receipt'] = self.receipt.to_json()

		return json


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
		return {
			'Email': self.email,
			'Phone': self.phone,
			'Taxation': self.taxation,
			'Items': [item.to_json() for item in self.receiptitem_set.all()]
		}

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
