from django.core.management import BaseCommand
from django.db.models import Q
from datetime import timedelta

from django.utils import timezone

from tinkoff_merchant.consts import PAYMENT_PAYED_STATUSES, CATEGORIES
from tinkoff_merchant.models import Payment
from tinkoff_merchant.services import MerchantAPI

DELTA = timedelta(days=30)
NOW = timezone.now()

class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        :type parser: argparse.ArgumentParser
        """
        parser.add_argument(
            '-D', '--description', dest='description',
            required=True,
            help='Description will be added to all new created payments',
            type=str
        )

        parser.add_argument(
            '-C', '--category', dest='category',
            required=True,
            help='Category will be added to all new payments items',
            type=str,
            choices=list(map(lambda x: x[0], CATEGORIES))
        )

        parser.add_argument(
            '-T', '--order-type-id', dest='order_type_id',
            required=True,
            help='order type will be included in new payments ids',
            type=int,
        )

    def handle(self, *args, **options):
        parent_payments = list(Payment.objects.filter(
            recurrent=True,
            status__in=PAYMENT_PAYED_STATUSES
        ).order_by('-creation_date'))

        api = MerchantAPI()

        charged_user_ids = set()
        for pp in parent_payments:
            # TODO: make this into payment object method
            # if we already have more recent parent payment
            if pp.customer_key in charged_user_ids:
                continue
            else:
                charged_user_ids.add(pp.customer_key)

            # if parent or children payment less than 30 days ago
            if ((NOW - pp.creation_date) < DELTA or
                    pp.children.filter(
                        creation_date__gt=NOW - DELTA,
                        status__in=PAYMENT_PAYED_STATUSES
                    ).exists()):
                continue

            print(f'\nCreating new children payment for {pp} -- {pp.amount/100}₽ -- {pp.creation_date.strftime("%Y-%m-%d")} -- {pp.user.username}')
            if pp.children.exists():
                print(f'{pp} has followed children payments')
                for child in pp.children.filter(status__in=PAYMENT_PAYED_STATUSES).order_by('creation_date'):
                    print(f'\t{child} -- {child.creation_date.strftime("%Y-%m-%d")}')

            new_payment = Payment.objects.create(
                parent=pp,
                description=options['description'],
                amount=pp.amount,
                customer_key=pp.customer_key
            ).with_receipt(
                email=pp.email,
            ).with_items(
                [dict(
                    name=options['description'],
                    price=pp.amount,
                    quantity=1,
                    amount=pp.amount,
                    category=options['category']
                )]
            )

            new_payment.order_id = '{0:02d}'.format(options["order_type_id"]) + '{0:06d}'.format(new_payment.id)

            new_payment = api.init(new_payment)
            if new_payment.success:
                new_payment = api.charge(new_payment)
                if new_payment.success:
                    print(f'SUCCESS -- {new_payment.status}')
                else:
                    print(f'ERROR -- {new_payment.status} -- {new_payment.error_code} -- {new_payment.message} -- {new_payment.details}')
            else:
                print(f'ERROR -- {new_payment.status} -- {new_payment.error_code} -- {new_payment.message} -- {new_payment.details}')
            new_payment.save()









