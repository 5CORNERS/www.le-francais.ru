from django.contrib import admin

from log_errors.models import ExceptionLog


# Register your models here.

@admin.register(ExceptionLog)
class ExceptionLogAdmin(admin.ModelAdmin):
    list_display = ['datetime', 'type', 'path', 'value', 'user']
    list_filter = ['type', 'datetime']
    search_fields = ['type', 'path', 'user__username', 'user__email']
    readonly_fields = [field.name for field in ExceptionLog._meta.fields]
