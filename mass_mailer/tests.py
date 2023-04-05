from collections import Counter
from datetime import timedelta, date
from pathlib import Path

from django.test import TestCase, override_settings
import freezegun
from django.utils import timezone

from custom_user.models import User
from mass_mailer.models import Message, UsersFilter, MessageLog
from tinkoff_merchant.consts import PAYMENT_STATUS_NEW, \
    PAYMENT_STATUS_CONFIRMED, PAYMENT_STATUS_AUTHORIZED
from tinkoff_merchant.models import Payment, Receipt, ReceiptItem


# Create your tests here.

def lists_equal_without_order(a, b):
    """
    This will make sure the inner list contain the same,
    but doesn't account for duplicate groups.
    """
    for l1 in a:
        check_counter = Counter(l1)
        if not any(Counter(l2) == check_counter for l2 in b):
            return False
    return True


@override_settings(
    MASS_EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend',
    EMAIL_FILE_PATH='temp/test_mails')
class MassMailerNewPaymentTest(TestCase):
    def setUp(self) -> None:
        self.new_payment_message = Message.objects.create(
            name='test',
            template_subject="Subject",
            template_txt="{{ filtered_payments.last.payment_url }}",
            template_html="{{ filtered_payments.last.payment_url }}",
            from_email="from@example.com",
            from_username="from_username",
            email_settings=None,
            validate_emails=False,
            recipients_filter=UsersFilter.objects.create(
                name='test',
                logged_more_than_once=False,
                payments_range_days=2,
                payments_statuses=[PAYMENT_STATUS_NEW],
                payments_range_days_b=1,
                payments_statuses_b=[PAYMENT_STATUS_NEW],
                payments_exclude_b=True,
                payments_statuses_c=[PAYMENT_STATUS_CONFIRMED,
                                     PAYMENT_STATUS_AUTHORIZED],
                payments_exclude_c=True,
                send_once=False,
                send_once_in_days=30,
            )
        )
        self.users = [
            User.objects.create(
                username='user1',
                email='user1@example.com'
            ),
            User.objects.create(
                username='user2',
                email='user2@example.com'
            ),
            User.objects.create(
                username='user3',
                email='user3@example.com'
            ),
            User.objects.create(
                username='user4',
                email='user4@example.com'
            ),
        ]

        with freezegun.freeze_time("2012-01-15 12:00"):
            for u in self.users:
                Payment.objects.create(
                    amount=1,
                    status=PAYMENT_STATUS_NEW,
                    creation_date=timezone.now(),
                    customer_key=str(u.pk),
                    payment_url='https://www.google.com',
                )

        with freezegun.freeze_time("2012-01-01 12:00"):
            # user4 paid successfully half a month ago
            Payment.objects.create(
                amount=1,
                status=PAYMENT_STATUS_CONFIRMED,
                creation_date=timezone.now(),
                customer_key=str(self.users[3].pk),
                payment_url='https://www.google.com',
            )

        with freezegun.freeze_time("2012-01-16 15:00"):
            # user3 tried to pay on the second day
            Payment.objects.create(
                amount=1,
                status=PAYMENT_STATUS_NEW,
                creation_date=timezone.now(),
                customer_key=str(self.users[2].pk),
                payment_url='https://www.google.com',
            )
            # user2 paid successfully on second day
            Payment.objects.create(
                amount=1,
                status=PAYMENT_STATUS_CONFIRMED,
                creation_date=timezone.now(),
                customer_key=str(self.users[1].pk),
                payment_url='https://www.google.com',
            )

    def test_sending(self):
        with freezegun.freeze_time("2012-01-16 18:00"):
            print(self.new_payment_message.send())

            self.assertTrue(lists_equal_without_order(
                MessageLog.objects.filter(
                    result__in=MessageLog.RESULTS_SUCCESS).values_list(
                    'recipient__username', flat=True),
                ['user1']
            ))

    def test_sending_second(self):
        with freezegun.freeze_time("2012-01-17 18:00"):
            sent, errors = self.new_payment_message.send()
            self.assertTrue(lists_equal_without_order(
                MessageLog.objects.filter(sent_datetime__date=date(2012, 1, 17),
                                          result__in=MessageLog.RESULTS_SUCCESS).values_list(
                    'recipient__username',
                    flat=True),
                ['user3']
            ))

    def test_sending_third(self):
        with freezegun.freeze_time("2012-01-18 18:00"):
            sent, errors = self.new_payment_message.send()
            self.assertEquals(sent, 0)

    def test_not_sending_after_new_payment(self):
        with freezegun.freeze_time("2012-01-19 12:00"):
            Payment.objects.create(
                amount=1,
                status=PAYMENT_STATUS_NEW,
                creation_date=timezone.now(),
                customer_key=str(self.users[0].pk),  # user1,
                payment_url='https://www.google.com',
            )
        with freezegun.freeze_time("2012-01-19 18:00"):
            sent, errors = self.new_payment_message.send()
            self.assertTrue('user1' not in MessageLog.objects.filter(
                sent_datetime__date=date(2012, 1, 20),
                result__in=MessageLog.RESULTS_SUCCESS
            ).values_list('recipient__username', flat=True))

    def test_sending_new_payment_after_1_month(self):
        with freezegun.freeze_time("2012-02-16 12:00"):
            Payment.objects.create(
                amount=1,
                status=PAYMENT_STATUS_NEW,
                creation_date=timezone.now(),
                customer_key=str(self.users[0].pk),  # user1,
                payment_url='https://www.google.com',
            )
        with freezegun.freeze_time("2012-02-17 18:00"):
            sent, errors = self.new_payment_message.send()
            self.assertTrue(lists_equal_without_order(
                MessageLog.objects.filter(
                    sent_datetime__date=date(2012, 2, 17),
                    result__in=MessageLog.RESULTS_SUCCESS).values_list(
                    'recipient__username',
                    flat=True),
                ['user1']
            ))
