from django.contrib import admin

# Register your models here.
from mass_mailer.models import Message, EmailSettings, UsersFilter, Profile, MessageLog


def send(modeladmin, request, qs):
	for q in qs:
		q.send()

def clear_sent(modeladmin, request, qs):
	for q in qs:
		q.sent.clear()

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	readonly_fields = ['sent']
	actions = [send, clear_sent]

@admin.register(EmailSettings)
class EmailSettings(admin.ModelAdmin):
	pass

@admin.register(UsersFilter)
class UsersFilterAdmin(admin.ModelAdmin):
	raw_id_fields = ['blacklist']

@admin.register(Profile)
class MailerProfileAdmin(admin.ModelAdmin):
	raw_id_fields = ['user']
	pass

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
	list_display = ['__str__', 'recipient', 'sent_datetime', 'result']
	readonly_fields = ['message', 'recipient', 'sent_datetime']
	pass
