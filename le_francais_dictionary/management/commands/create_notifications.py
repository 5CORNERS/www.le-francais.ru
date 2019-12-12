import datetime
import pytz
from django.core.management import BaseCommand

from django.urls import reverse
from django.utils import timezone
from pybb.models import Profile

from notifications.models import Notification, NotificationUser, \
	NotificationImage
from le_francais_dictionary.models import UserWordRepetition
from custom_user.models import User  # FIXME use get_user_model


class Command(BaseCommand):
	def handle(self, *args, **options):
		create_notifications()


def create_notifications():
	today_repetitions = UserWordRepetition.objects.filter(
		repetition_date=timezone.now().date())
	users = User.objects.filter(pk__in=[r.user_id for r in today_repetitions])
	profile = Profile.objects.get(pk=727)
	for u in users:
		tz = u.timezone or 'UTC'
		if timezone.make_naive(timezone.now(),
		                       pytz.timezone(tz)).hour == datetime.time(0, 0,
		                                                                0).hour:
			notification = Notification(
				image=NotificationImage.objects.get_or_create(
					url=profile.avatar_url
				)[0],
				title='Новые слва для повторения',
				category=Notification.INTERVAL_REPETITIONS,
				data=dict(
					url=reverse('dictionary:app_repeat')
				),
				click_url=reverse('dictionary:app_repeat'),
				content_object=next(
					r for r in today_repetitions if r.user_id == u.pk)
			)
			notification.save()
			NotificationUser.objects.get_or_create(
				notification=notification,
				user=u
			)
