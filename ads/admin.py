from django.contrib import admin

# Register your models here.
from ads.models import LineItem, Placement, Creative


class CreativeInline(admin.TabularInline):
    model = Creative
    fk_name = 'line_item'
    extra = 5
    readonly_fields = ['views', 'clicks']


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    readonly_fields = ['views', 'clicks']
    inlines = [CreativeInline]

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    pass

