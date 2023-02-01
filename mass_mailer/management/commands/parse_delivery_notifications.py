import email
from email.utils import parseaddr
import json
import re
from pathlib import Path
from zipfile import ZipFile

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from user_sessions.models import Session

from mass_mailer.models import Profile

User = get_user_model()
FEEDBACK_FIELDS_REQ = [
	'Feedback-Type',
	'User-Agent',
	'Version'
]
FEEDBACK_FIELDS_OPT = [
	'Original-Envelope-Id',
	'Original-Mail-From',
	'Arrival-Date',
	'Reporting-MTA',
	'Source-IP',
	'Incidents',
	'Source'
]
FEEDBACK_FIELDS_MULTIPLE= [
	'Authentication-Results',
	'Original-Rcpt-To',
	'Reported-Domain',
	'Reported-URI'
]

DSN_FIELDS = [
	'Original-Envelope-Id',
	'Reporting-MTA',
	'DSN-Gateway',
	'Received-From-MTA',
	'Arrival-Date',
	'Original-Recipient',
	'Final-Recipient',
	'Action',
	'Status',
	'Remote-MTA',
	'Diagnostic-Code',
	'Last-Attempt-Date',
	'Final-Log-ID',
	'Will-Retry-Until',
]

EMAIL_HEADERS = [
	'Original-Mail-From',
	'Original-Rcpt-To',
	'Original-Recipient',
	'Final-Recipient',
]

class Command(BaseCommand):
	def handle(self, *args, **options):
		recipients_to_filter_out = []
		stats = {}
		emls = get_emls_from_zips('mass_mailer/temp/to_parse_jsons')
		for eml in emls:
			msg = email.message_from_bytes(eml)
			for part in msg.walk():
				if part.get_content_type() == 'text/plain':
					body = part.get_payload()
					try:
						data = json.loads(body)
						data['Message'] = json.loads(data['Message'])
						notification_type = data['Message']['notificationType']
						if notification_type in stats.keys():
							stats[notification_type]['count'] += 1
						else:
							stats[notification_type] = {'count': 1, 'subs': {}, 'types': {}, 'notifications': []}

						if notification_type == 'Complaint':
							complaint_data = data['Message']['complaint']
							complaint_sub_type = complaint_data.get('complaintSubType')
							feedback_type = complaint_data.get('complaintFeedbackType')
							count_to_dict(complaint_sub_type, stats[notification_type]['subs'])
							count_to_dict(feedback_type, stats[notification_type]['types'])
							user_agent = complaint_data.get('userAgent')

							complaint_datetime = complaint_data.get('arrivalDate', complaint_data.get('timestamp'))

							recipients = [r['emailAddress'] for r in complaint_data.get('complainedRecipients', [])]
							for r in recipients:
								userdata = self.get_user_data(r)
								stats[notification_type][
									'notifications'].append(
										{
											'email': r,
											'timestamp': complaint_datetime,
											'feedback_type': feedback_type,
											'user_agent': user_agent,
											'user': userdata,
											'description': complaint_sub_type
										}
									)
							recipients_to_filter_out = recipients_to_filter_out + recipients

						elif notification_type == 'Bounce':
							bounce_data = data['Message']['bounce']
							bounce_type = bounce_data.get('bounceType')
							bounce_sub_type = bounce_data.get('bounceSubType')
							count_to_dict(bounce_type, stats[notification_type]['types'])
							count_to_dict(bounce_sub_type, stats[notification_type]['subs'])

							if bounce_type == 'Permanent':
								for r in bounce_data.get('bouncedRecipients', []):
									recipient_email = r['emailAddress']
									try:
										description = r['diagnosticCode']
									except KeyError:
										description = ''
									userdata = self.get_user_data(recipient_email)
									recipients_to_filter_out.append(recipient_email)
									stats[notification_type][
										'notifications'].append(
										{
											'email': recipient_email,
											'timestamp': data['Message']['mail'].get('timestamp'),
											'feedback_type': bounce_sub_type,
											'user': userdata,
											'description': description
										}
										)

					except json.JSONDecodeError:
						pass
		print(json.dumps(stats, indent=4, default=str), end='\n\n')

		stats_yandex = {}
		old_emls = get_emls_from_zips('mass_mailer/temp/to_parse')
		old_recipients_to_filter_out = []
		for eml in old_emls:
			msg = email.message_from_bytes(eml)
			for part in msg.walk():
				if part.get_content_type() == 'message/delivery-status':
					body = part.get_payload()
					for body_part in body:
						original_recipient = body_part.get("Original-Recipient")
						status = body_part.get("Status")
						if original_recipient is not None and status.split('.')[0] == "5":
							original_recipient = original_recipient.split(";")[-1]
							old_recipients_to_filter_out.append(original_recipient)
							if status not in stats_yandex.keys():
								stats_yandex[status] = {
									'code': status,
									'description': body_part.get('Diagnostic-Code'),
									'recipients': [original_recipient],
								}
							else:
								stats_yandex[status]['recipients'].append(original_recipient)

		print(json.dumps(stats_yandex, indent=4))

		with open('mass_mailer/temp/result_yandex.json', 'w', encoding='utf-8') as f:
			json.dump(stats_yandex, f, indent=4, default=str)

		with open('mass_mailer/temp/result.json', 'w', encoding='utf-8') as f:
			json.dump(stats, f, indent=4, default=str)

		recipients_to_filter_out = set(recipients_to_filter_out + old_recipients_to_filter_out)
		for recipient in recipients_to_filter_out:
			print(recipient)
			try:
				user = User.objects.get(email=recipient)
				mailer_profile:Profile = user.mailer_profile
				mailer_profile.subscribed = False
			except User.DoesNotExist:
				mailer_profile, is_new = Profile.objects.get_or_create(
					_email=recipient,
				)
				mailer_profile.subscribed = False
			# mailer_profile.save(update_fields=['subscribed'])

	def get_user_data(self, email):
		try:
			user = User.objects.get(email=email)
			userdata = {
				'username': user.username,
				'cups': user.cups_amount,
				'last_login': user.last_login,
				'registered': user.date_joined,
				'country': user.country_name
			}
			try:
				last_session = Session.objects.get(user=user)
				last_session_data = {
					'last_activity': last_session.last_activity,
					'ip': last_session.ip,
					'user_agent': last_session.user_agent,
				}
			except Session.DoesNotExist:
				last_session_data = None
			userdata['session_data'] = last_session_data
		except User.DoesNotExist:
			userdata = None
		return userdata


def get_emls_from_zips(path):
	emls = []
	for zip_path in Path(path).glob('*.zip'):
		with ZipFile(zip_path, 'r') as f:
			for name in f.namelist():
				emls.append(f.read(name))
	return emls


def count_to_dict(k, d:dict):
	if k in d.keys():
		d[k] += 1
	else:
		d[k] = 1

def parse_dsn(s):
	result = {}
	for header_name in DSN_FIELDS:
		result[header_name] = get_header_value(header_name, s)
	return result

def parse_feedback(s):
	result = {}
	for header_name in FEEDBACK_FIELDS_REQ + FEEDBACK_FIELDS_OPT:
		result[header_name] = get_header_value(header_name, s)
	for header_name in FEEDBACK_FIELDS_MULTIPLE:
		result[header_name] = get_header_value(header_name, s, multiple=True)
	return result

def parse_mail(s):
	# if ";" in s:
	# 	display_name, address = parseaddr(s.split(';')[1])
	# else:
	# 	display_name, address = parseaddr(s)
	return s

def get_header_value(header_name, s, parse_email=False, multiple=False):
	if header_name in EMAIL_HEADERS:
		parse_email = True
	pattern = re.compile(f'^(?:{header_name}:\s?)(.*)$', re.M|re.I)
	if multiple:
		l = []
		for match in re.finditer(pattern, s):
			if match:
				if parse_email:
					header_value = parse_mail(match.group(1))
				else:
					header_value = match.group(1)
				l.append(header_value)
		return l
	else:
		match = re.search(pattern, s)
		if match:
			header_value = match.group(1)
		else:
			return None
		if parse_email:
			header_value = parse_mail(header_value)
	return header_value

