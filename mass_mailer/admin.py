from django.contrib import admin

# Register your models here.
from mass_mailer.models import Message, EmailSettings, UsersFilter, Profile


def send(modeladmin, request, qs):
	for q in qs:
		q.send()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	readonly_fields = ['sent']
	actions = [send]

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
