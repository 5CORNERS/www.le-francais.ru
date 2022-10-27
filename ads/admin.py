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
    form = GeoAdder

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    pass

@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    pass
