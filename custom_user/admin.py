from django.contrib import admin

from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
	list_display = ['username', 'email', 'date_joined', 'must_pay', 'saw_message', '_cup_amount', '_cup_credit', '_low_price', 'is_active']
	list_filter = ['date_joined']
	search_fields = ['username', 'email', 'first_name', 'last_name']
