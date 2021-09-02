from email.message import Message
from email.utils import formataddr

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import URLField
from django.dispatch import receiver

from tinkoff_merchant.signals import payment_confirm

User = get_user_model()

DONATION_TARGET_LIFE = 1
DONATION_TARGET_ADS = 2
DONATION_TARGETS_CHOICES = [
    (DONATION_TARGET_LIFE, 'на хлеб насущный'),
    (DONATION_TARGET_ADS, 'на рекламу проекта')
]


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
    email = models.EmailField(
        null=True, default=None, blank=True
    )
    comment = models.TextField(
        null=True, default=None, blank=True
    )
    target = models.PositiveSmallIntegerField(
        choices=DONATION_TARGETS_CHOICES, default=DONATION_TARGET_LIFE
    )

    def __init__(self, *args, **kwargs):
        super(Donation, self).__init__(*args, **kwargs)
        self._recurrent = None

    @property
    def recurrent(self):
        if self._recurrent is None:
            self._recurrent = self.payment.recurrent
        return self._recurrent


@receiver(payment_confirm)
def send_support_notification(sender, **kwargs):
    donation = kwargs['payment'].donation_set.first()
    if donation is not None and isinstance(donation, Donation):

        user = None
        if donation.user:
            user = user
        else:
            if donation.email:
                try:
                    user = User.objects.get(email=donation.email)
                except User.DoesNotExist:
                    pass
            if donation.payment.email and user is None:
                try:
                    user = User.objects.get(email=donation.payment.email)
                except User.DoesNotExist:
                    pass

        user_email = None
        if donation.email:
            user_email = donation.email
        elif user is not None:
            user_email = user.email
        elif donation.payment.email:
            user_email = donation.payment.email

        if user_email:
            reply_to = formataddr(pair=(None, user_email))
        else:
            reply_to = None

        if user:
            if user.first_name:
                name = user.get_full_name()
            else:
                name = user.get_username()
        elif donation.email:
            name = donation.email
        else:
            name = 'Человек, пожелавший остаться неизвестным,'

        if donation.target == DONATION_TARGET_LIFE:
            target_description = 'на хлеб насущный'
        elif donation.target == DONATION_TARGET_ADS:
            target_description = 'на рекламу проекта'
        else:
            target_description = 'на неизвестную цель'

        EmailMessage(
            subject='Помощь проекту le-francais.ru',
            body=f'{name} только что пожертвовал(а) проекту {donation.amount / 100} рублей {target_description}.\n'
                 f'\n'
                 f'Комментарий к пожертвованию:\n'
                 f'{donation.comment}',
            to=formataddr(('ILYA DUMOV', 'ilia.dumov@gmail.com')),
            reply_to=reply_to
        ).send()

    else:
        pass
