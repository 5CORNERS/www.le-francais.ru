import csv

from django.contrib import admin
from django.http import HttpResponse

# Register your models here.
from ads.forms import GeoAdder
from ads.models import LineItem, Placement, Creative, Log


class CreativeInline(admin.TabularInline):
    model = Creative
    fk_name = 'line_item'
    extra = 0
    readonly_fields = ['views', 'clicks']


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    readonly_fields = ['views', 'clicks']
    inlines = [CreativeInline]
    fields = [
        'name', 'priority', 'placements', 'placements_inverted',
        'placements_and', 'placements_and_inverted',
        'ad_units',
        'do_not_show_to',
        'less_than_n_days_ago',
        'less_than_n_days_ago_value',
        'do_not_show_if_was_on_conjugations',
        'views',
        'clicks',
        'capping_day',
        'capping_week',
        'capping_month',
        'do_not_display_to_registered_users',
        'do_not_display_to_anonymous_users',
        'labels',
        'targeting_country',
        'targeting_city',
        'targeting_invert',
        'disable', 'utm_campaign', 'utm_medium',
        'do_not_display_to_donating_users',
        'do_not_display_to_donating_users_days_ago',
        'display_to_paying_users',
        'do_not_display_to_paying_users',
    ]
    # form = GeoAdder

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    pass

@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    pass

def export_csv(modeladmin, request, queryset):
    response = HttpResponse(
        content_type='text/csv',
    )
    response['Content-Disposition'] = 'attachment; filename="export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Datetime',
        'Clicked',
        'Line Item',
        'Creative Name',
        'Creative Size',
        'Ad Unit Name',
        'Ad Unit Placements',
        'Username',
        'IP',
        'Country',
        'City',
    ])
    for log_object in queryset.select_related('line_item', 'creative'):
        log_object: Log
        if log_object.user is not None:
            username = log_object.user.username
        else:
            username = ''
        if log_object.ad_unit_placements:
            placements_str = ", ".join(log_object.ad_unit_placements)
        else:
            placements_str = ''
        writer.writerow([
            log_object.datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
            log_object.clicked,
            log_object.line_item.name,
            log_object.creative.name,
            f'{log_object.creative.width}x{log_object.creative.height}',
            log_object.ad_unit_name,
            placements_str,
            username,
            log_object.ip,
            log_object.country,
            log_object.city
        ])
    return response

export_csv.short_description = "Export CSV"


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = [
        'datetime',
        'clicked',
        'line_item',
        'creative',
        'user',
        'country',
        'city',
    ]
    list_filter = ['line_item', 'datetime', 'clicked']
    readonly_fields = [field.name for field in Log._meta.fields]

    actions = [export_csv]
