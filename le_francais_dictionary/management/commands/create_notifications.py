import datetime
import pytz
from bulk_update.helper import bulk_update
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
					qty=len(r.repetitions)
				),
				click_url=reverse('dictionary:app_repeat'),
				content_object=r,
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
