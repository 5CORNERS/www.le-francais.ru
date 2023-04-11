from django.contrib import admin

# Register your models here.
from mass_mailer.models import Message, EmailSettings, UsersFilter, Profile, MessageLog
from django.contrib.admin import DateFieldListFilter

def send(modeladmin, request, qs):
	for q in qs:
		q.send()

def clear_sent(modeladmin, request, qs):
	for q in qs:
		q.sent.clear()

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	readonly_fields = ['sent']
	raw_id_fields = ['postman_sender']
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
	list_display = ['__str__', 'subscribed', 'status']
	list_filter = ['status', 'subscribed']
	search_fields = ['_email', 'user__username']

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
	list_display = ['__str__', 'recipient', 'sent_datetime', 'result']
	readonly_fields = ['message', 'recipient', 'sent_datetime']
	list_filter = ['message', ('sent_datetime', DateFieldListFilter), 'result']
	search_fields = ['message__name', 'recipient__username', 'recipient__email']
	pass
