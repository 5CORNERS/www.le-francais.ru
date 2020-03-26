from django.contrib import admin

# Register your models here.
from mass_mailer.models import Message, EmailSettings, UsersFilter


def send(modeladmin, request, qs):
	for q in qs:
		q.send()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	readonly_fields = ['sent']
	actions = [send]
	pass

@admin.register(EmailSettings)
class EmailSettings(admin.ModelAdmin):
	pass

@admin.register(UsersFilter)
class UsersFilterAdmin(admin.ModelAdmin):
	pass
