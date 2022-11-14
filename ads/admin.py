from django.contrib import admin

# Register your models here.
from ads.forms import GeoAdder
from ads.models import LineItem, Placement, Creative, Log


class CreativeInline(admin.TabularInline):
    model = Creative
    fk_name = 'line_item'
    extra = 0
    readonly_fields = ['views', 'clicks', 'width', 'height']


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    readonly_fields = ['views', 'clicks']
    inlines = [CreativeInline]
    fields = [
        'name', 'priority', 'placements', 'placements_inverted', 'ad_units',
        'do_not_show_to',
        'do_not_show_if_was_on_conjugations',
        'views',
        'clicks',
        'capping_day',
        'capping_week',
        'capping_month',
        'do_not_display_to_registered_users',
        'labels',
        'targeting_country',
        'targeting_city',
        'targeting_invert',
        'disable', 'utm_campaign', 'utm_medium'
    ]
    # form = GeoAdder

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    pass

@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    pass

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
