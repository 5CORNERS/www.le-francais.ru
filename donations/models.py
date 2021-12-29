from email.utils import formataddr

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db import models
from django.dispatch import receiver

from tinkoff_merchant.signals import payment_confirm

User = get_user_model()

DONATION_TARGET_LIFE = 1
DONATION_TARGET_ADS = 2
DONATION_TARGET_CROWDFUNDING = 3
DONATION_TARGETS_CHOICES = [
    (DONATION_TARGET_LIFE, 'на хлеб насущный'),
    (DONATION_TARGET_ADS, 'на рекламу проекта'),
    (DONATION_TARGET_CROWDFUNDING, 'на дооснащение студии')
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

    def send_email_notification(self):
        if self.user is not None:
            user = self.user
        elif self.email:
            try:
                user = User.objects.get(email=self.email)
            except User.DoesNotExist:
                user = None
        else:
            user = None

        if self.email:
            user_email = self.email
        elif user is not None:
            user_email = user.email
        else:
            user_email = None

        if user_email is not None:
            reply_to = formataddr(pair=(None, user_email))
        else:
            reply_to = None

        if user:
            if user.first_name:
                name = user.get_full_name()
            else:
                name = user.get_username()
        elif self.email:
            name = self.email
        else:
            name = 'Человек, пожелавший остаться неизвестным,'

        if self.target == DONATION_TARGET_LIFE:
            target_description = 'на хлеб насущный'
        elif self.target == DONATION_TARGET_ADS:
            target_description = 'на рекламу проекта'
        else:
            target_description = 'на неизвестную цель'

        EmailMessage(
            subject='Помощь проекту le-francais.ru',
            body=f'{name} только что пожертвовал(а) проекту {message(self.amount)} {target_description}.\n'
                 f'\n'
                 f'Комментарий к пожертвованию:\n'
                 f'{self.comment}',
            to=[formataddr(('ILYA DUMOV', 'ilia.dumov@gmail.com'))],
            reply_to=[reply_to] if reply_to else None
        ).send()


def message(n, form1='рубль', form2='рубля', form5='рублей'):
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return '{0} {1}'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return '{0} {1}'.format(str(n), form2)
    else:
        return '{0} {1}'.format(str(n), form5)


@receiver(payment_confirm)
def send_support_notification(sender, **kwargs):
    donation = kwargs['payment'].donation_set.first()
    if donation is not None and isinstance(donation, Donation):
        donation.send_email_notification()
    else:
        pass
