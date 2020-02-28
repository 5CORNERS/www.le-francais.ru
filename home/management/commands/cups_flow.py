from datetime import timedelta

from django.core.management import BaseCommand
from django.db.models import Sum, Q
from django.utils import timezone

from custom_user.models import User
from home.models import UserLesson
from tinkoff_merchant.models import ReceiptItem as TinkoffCups


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def print_cups_flow():
	print('DATE', 'CUPS REMAINS', 'CUPS IN', 'CUPS OUT', sep='\t')
	start_year = 2019
	stat_month = 1
	start_day = 1
	start_date = timezone.datetime(start_year, stat_month, start_day).date()
	end_date = timezone.now().date()
	start_cups = 0
	for single_date in daterange(start_date, end_date):
	    cups_plus = TinkoffCups.objects.filter(Q(receipt__payment__status='CONFIRMED') | Q(receipt__payment__status='AUTHORIZED'), receipt__payment__creation_date__date=single_date).distinct().aggregate(Sum('site_quantity'))['site_quantity__sum'] or 0
	    cups_minus = UserLesson.objects.filter(date__date=single_date).count() or 0
	    end_cups = start_cups + cups_plus - cups_minus
	    print(single_date.strftime('%Y-%m-%d'), end_cups, cups_plus, cups_minus, sep='\t')
	    start_cups = int(end_cups)

class Command(BaseCommand):
	def handle(self, *args, **options):
		print_cups_flow()
