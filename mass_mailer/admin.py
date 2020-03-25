from django.contrib import admin

# Register your models here.
from mass_mailer.models import Message, EmailSettings, UsersFilter


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	pass

@admin.register(EmailSettings)
class EmailSettings(admin.ModelAdmin):
	pass

@admin.register(UsersFilter)
class UsersFilterAdmin(admin.ModelAdmin):
	pass
