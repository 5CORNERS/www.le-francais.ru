from django.contrib import admin

# Register your models here.
from ads.forms import GeoAdder
from ads.models import LineItem, Placement, Creative


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
        'name', 'priority', 'placements', 'ad_units',
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
        'disable'
    ]
    # form = GeoAdder

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    pass

@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    pass
