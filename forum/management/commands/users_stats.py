from django.core.management import BaseCommand

from custom_user.models import User
from pybb.models import Profile


class Command(BaseCommand):
	def handle(self, *args, **options):
		print(u"Mail\tNickname\tPost Count\tRegistration\tLast Visit")
		for user in User.objects.all():
			profile = Profile.objects.get(user=user)
			print(str(user.email) + '\t' + str(user.username) + '\t' + str(profile.post_count) + '\t' + str(
				user.date_joined.strftime("%Y-%m-%d %H:%M")) + '\t' + str(user.last_login.strftime("%Y-%m-%d %H:%M")))
