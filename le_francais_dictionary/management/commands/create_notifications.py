import datetime
import pytz
from bulk_update.helper import bulk_update
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from django.urls import reverse
from django.utils import timezone
from pybb.models import Profile

from notifications.models import Notification, NotificationUser, \
	NotificationImage
from le_francais_dictionary.models import UserDayRepetition
from custom_user.models import User  # FIXME use get_user_model


class Command(BaseCommand):
	def handle(self, *args, **options):
		create_notifications()


def message(n, form1=' новое слово', form2=' новых слова', form5=' новых слов'):
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return '{0} {1}'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return '{0} {1}'.format(str(n), form2)
    else:
        return '{0} {1}'.format(str(n), form5)


# TODO move it to notifications app
def create_notifications():
	profile = Profile.objects.get(pk=727)
	now_repetitions = UserDayRepetition.objects.filter(
		datetime__day=timezone.now().day, datetime__hour=timezone.now().hour)
	for r in now_repetitions:
		try:
			notification, created = Notification.objects.get_or_create(
				image=NotificationImage.objects.get_or_create(
					url=profile.avatar_url
				)[0],
				title='Доступны новые слова для повторения',
				category=Notification.INTERVAL_REPETITIONS,
				data=dict(
					url=reverse('dictionary:app_repeat'),
					quantity_message=message(len(r.repetitions))
				),
				click_url=reverse('dictionary:app_repeat'),
				content_type=ContentType.objects.get_for_model(r),
				object_id=r.pk
			)
			NotificationUser.objects.get_or_create(
				notification=notification,
				user=r.user
			)
			r.success = True
			r.save()
		except:
			r.success = False
			r.save()
			print(f'Error creating notification {r.pk}')
