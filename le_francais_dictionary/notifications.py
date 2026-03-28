from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from pybb.models import Profile

from le_francais_dictionary.models import UserDayRepetition, get_repetition_words_query
from notifications.models import Notification, NotificationImage, NotificationUser


def create_dictionary_notification(sender, instance: UserDayRepetition, **kwargs):
	try:
		site_forum_profile = Profile.objects.get(pk=727).avatar_url
		image_url = Profile.objects.get(pk=727).avatar_url
	except Profile.DoesNotExist:
		image_url = 'https://www.le-francais.ru/static/images/cat_logo.png'
	from le_francais_dictionary.utils import message
	all_repetitions_count = get_repetition_words_query(instance.user).count()
	if all_repetitions_count != len(instance.repetitions):
		all_message = f' (всего их {all_repetitions_count})'
	else:
		all_message = ''
	notification, created = Notification.objects.get_or_create(
		image=NotificationImage.objects.get_or_create(
			url=image_url
		)[0],
		title='Доступны новые слова для повторения',
		category=Notification.INTERVAL_REPETITIONS,
		data=dict(
			url=reverse('dictionary:app_repeat'),
			quantity_message=message(len(instance.repetitions)),
			all=all_message
		),
		click_url=reverse('dictionary:app_repeat'),
		content_type=ContentType.objects.get_for_model(UserDayRepetition),
		object_id=instance.pk
	)
	if created:
		print(f'Created Notification {notification.datetime_creation} -- {len(instance.repetitions)}')
	try:
		NotificationUser.objects.get_or_create(
			notification=notification,
			user=instance.user
		)
	except NotificationUser.MultipleObjectsReturned:
		NotificationUser.objects.filter(
			notification=notification,
			user=instance.user
		)[1:].delete()
