from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import User


class CustomUserChangeForm(UserChangeForm):
	class Meta(UserChangeForm.Meta):
		model = User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	form = CustomUserChangeForm

	fieldsets = UserAdmin.fieldsets + (
		(None, {'fields': ('cup_amount',)}),
	)
