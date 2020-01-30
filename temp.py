from django.db.models import Q

from custom_user.models import User, LogMessage
import csv

from home.models import UserLesson
from le_francais_dictionary.models import UserWordRepetition
from tinkoff_merchant.models import Payment

with open('users.csv', 'w', encoding='utf-8') as f:
	csv_writer = csv.writer(f, csv.excel_tab)
	csv_writer.writerow(
		['Email', 'Username', 'First Name', 'Last Name', 'Recent Login',
		 'Registration', 'Likes', 'Posts', 'Orders', 'Payments', 'Last Payment',
		 'Last Payment Activation', 'Downloads', 'Last DL',
		 'Activated', 'Last Activated', 'Cards', 'ReCaptcha'])
	for user in User.objects.prefetch_related('pybb_profile', 'session_set',
	                                          'pybb_profile__like_set',
	                                          'payment').all():
		print(user)
		download_count = LogMessage.objects.filter(user=user).count()
		if download_count > 0:
			last_dl = LogMessage.objects.filter(user=user).order_by(
				'-datetime').first().datetime
		else:
			last_dl = None
		payment_amount = 0
		had_orders = Payment.objects.filter(customer_key=user.pk).exists()
		if had_orders:
			for payment in Payment.objects.filter(customer_key=user.pk).filter(Q(status='CONFIRMED') | Q(status='AUTHORIZED')):
				payment_amount += payment.amount / 100
		last_payment = Payment.objects.order_by('-update_date').filter(customer_key=user.pk).first()
		if last_payment:
			last_payment = last_payment.update_date
		else:
			last_payment = None
		last_payment_activation = None
		if last_payment:
			try:
				last_payment_activation = last_payment.closest_activation
			except:
				last_payment_activation = None
		activated = list(UserLesson.objects.select_related('lesson').filter(user=user).order_by('-date'))
		activated_count = len(activated)
		last_activated = None
		if activated_count > 0:
			last_activated = activated[0].lesson.lesson_number
		session = user.session_set.order_by('-last_activity').first()
		if session:
			last_activity = session.last_activity
		else:
			last_activity = None
		cards = UserWordRepetition.objects.filter(user=user).count()
		csv_writer.writerow(
			[user.email, user.username, user.first_name, user.last_name,
			 last_activity,
			 user.date_joined, user.pybb_profile.like_set.all().count(),
			 user.posts.all().count(), had_orders,
			 payment_amount, last_payment, last_payment_activation,
			 download_count, last_dl, activated_count, last_activated, cards,
			 user.recaptcha3_score
			 ])
