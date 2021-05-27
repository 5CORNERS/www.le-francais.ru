from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import URLField

User = get_user_model()


class Donation(models.Model):
	amount = models.IntegerField()
	payment = models.ForeignKey(
		'tinkoff_merchant.Payment',
		on_delete=models.PROTECT
	)
	datetime_creation = models.DateTimeField(auto_now_add=True)
	cancelled = models.BooleanField(default=False)
	user = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		default=None
	)

	def __init__(self, *args, **kwargs):
		super(Donation, self).__init__(*args, **kwargs)
		self._recurrent = None

	@property
	def recurrent(self):
		if self._recurrent is None:
			self._recurrent = self.payment.recurrent
		return self._recurrent
