import pandas as pd
from django.core.management import BaseCommand
from django.core.files import File
from custom_user.models import User
from pybb.models import Profile


class Command(BaseCommand):
	def handle(self, *args, **options):
		with open('forum/avatars.csv', 'r') as f:
			df = pd.read_csv(f)
			table = df.to_dict()
		for i in range(len(table['Email'])):
			user = User.objects.get(email=table['Email'][i])
			image_id = table['Image ID'][i]
			if image_id == "Unresolved":
				print("unresolved avatar: " + user.email)
				continue
			avatar = File(open('forum/avatars/' + image_id + '.jpg', 'rb'))
			user.pybb_profile.avatar.save(image_id+'.jpg', avatar, save=True)
			user.profile.save()
			print('success ' + user.email + ' ' + image_id)
