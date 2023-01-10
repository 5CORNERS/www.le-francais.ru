import email
from email.utils import parseaddr
import json
import re
from pathlib import Path
from zipfile import ZipFile

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

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
							stats[notification_type] = {'count': 1, 'subs': {}, 'types': {}}

						if notification_type == 'Complaint':
							complaint_data = data['Message']['complaint']
							complaint_sub_type = complaint_data.get('complaintSubType')
							complaint_feedback_type = complaint_data.get('complaintFeedbackType')
							count_to_dict(complaint_sub_type, stats[notification_type]['subs'])
							count_to_dict(complaint_feedback_type, stats[notification_type]['types'])

							recipients = [r['emailAddress'] for r in complaint_data.get('complaintRecipients', [])]
							recipients_to_filter_out = recipients_to_filter_out + recipients

						elif notification_type == 'Bounce':
							bounce_data = data['Message']['bounce']
							bounce_type = bounce_data.get('bounceType')
							bounce_sub_type = bounce_data.get('bounceSubType')
							count_to_dict(bounce_type, stats[notification_type]['types'])
							count_to_dict(bounce_sub_type, stats[notification_type]['subs'])

							recipients = [r['emailAddress'] for r in bounce_data.get('bouncedRecipients', [])]

							if bounce_type == 'Permanent':
								recipients_to_filter_out = recipients_to_filter_out + recipients

					except json.JSONDecodeError:
						pass
		print(json.dumps(stats, indent=4))

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
							old_recipients_to_filter_out.append(original_recipient.split(";")[-1])

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
			mailer_profile.save(update_fields=['subscribed'])


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

