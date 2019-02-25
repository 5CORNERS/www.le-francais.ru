from django.core.management import BaseCommand
from pandas import read_csv
from custom_user.models import User

class Command(BaseCommand):
	def handle(self, *args, **options):
		table = read_csv('html_files/dialogs/add_tickets.csv')
		not_exist, exist = [], []
		for index, row in table.iterrows():
			mail = row['MAIL']
			n = row['TICKETS']
			try:
				user = User.objects.get(email=mail)
				exist.append(user)
			except:
				not_exist.append(row['MAIL'])
				continue
			user.add_cups(n)
		print('\nНайдено {0} пользователей:'.format(len(exist)))
		for user in exist:
			print('{0} {1} {2} {3}'.format(user.email, user.username, user.first_name, user.last_name))
		print('\nНе найдено {0} пользователей:'.format(len(not_exist)))
		for mail in not_exist:
			print(mail)