from django.core.management import BaseCommand
from django.utils import timezone

from mass_mailer.models import Message


class Command(BaseCommand):
	def handle(self, *args, **options):
		print(f'Sending "Mass Mailer" messages...')
		filtered_messages = [message for message in Message.objects.filter(
			send_datetime__lte=timezone.now()) if message.get_recipients()]
		print(f'Filtered {len(filtered_messages)} messages.')
		for message in filtered_messages:
			print(f'\tSending "{message}" to {len(message.get_recipients())} users...')
			sent_count, errors_count = message.send()
			print(f'\tSuccessfully sent to {sent_count} recipients.')
			if errors_count:
				print(f'\tFailed sending to {errors_count} recipients, see messages logs for details.\n')
