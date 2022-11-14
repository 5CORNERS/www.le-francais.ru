from django.contrib import admin

from log_errors.models import ExceptionLog


# Register your models here.

class ExcludeTypeFilter(admin.SimpleListFilter):
    title = 'exclude type'
    parameter_name = 'exclude'

    def lookups(self, request, model_admin):
        return (
            ('http404', 'Http404'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'http404':
            return queryset.exclude(type='Http404')

@admin.register(ExceptionLog)
class ExceptionLogAdmin(admin.ModelAdmin):
    list_display = ['datetime', 'type', 'path', 'value', 'user']
    list_filter = [ExcludeTypeFilter, 'type', 'datetime']
    search_fields = ['type', 'path', 'user__username', 'user__email']
    readonly_fields = [field.name for field in ExceptionLog._meta.fields]
