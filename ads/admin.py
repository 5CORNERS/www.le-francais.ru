import csv

from django.contrib import admin
from django.db.models import Q, Subquery, OuterRef, Count, IntegerField
from django.http import HttpResponse

# Register your models here.
from ads.forms import GeoAdder
from ads.models import LineItem, Placement, Creative, Log


class CreativeInline(admin.TabularInline):
    model = Creative
    fk_name = 'line_item'
    extra = 0
    readonly_fields = ['combined_views', 'combined_clicks', 'views', 'clicks']

    def get_queryset(self, request):
        qs = super(CreativeInline, self).get_queryset(request)
        active_views_subquery = Log.objects.filter(creative=OuterRef('pk')).values('creative').annotate(c=Count('id')).values('c')
        active_clicks_subquery = Log.objects.filter(creative=OuterRef('pk'), clicked=True).values('creative').annotate(c=Count('id')).values('c')
        return qs.annotate(
            active_views=Subquery(active_views_subquery, output_field=IntegerField()),
            active_clicks=Subquery(active_clicks_subquery, output_field=IntegerField())
        )

    def combined_views(self, obj):
        active_views = getattr(obj, 'active_views', None)
        if active_views is None:
            active_views = Log.objects.filter(creative=obj).count()
        return obj.views + (active_views or 0)
    combined_views.short_description = 'Combined Views'

    def combined_clicks(self, obj):
        active_clicks = getattr(obj, 'active_clicks', None)
        if active_clicks is None:
            active_clicks = Log.objects.filter(creative=obj, clicked=True).count()
        return obj.clicks + (active_clicks or 0)
    combined_clicks.short_description = 'Combined Clicks'


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    form = GeoAdder
    readonly_fields = ['combined_views', 'combined_clicks', 'views', 'clicks']
    inlines = [CreativeInline]
    fields = [
        'name', 'priority', 'placements', 'placements_inverted',
        'placements_and', 'placements_and_inverted',
        'ad_units',
        'do_not_show_to',
        'less_than_n_days_ago',
        'less_than_n_days_ago_value',
        'do_not_show_if_was_on_conjugations',
        'combined_views',
        'combined_clicks',
        'views',
        'clicks',
        'capping_day',
        'capping_week',
        'capping_month',
        'do_not_display_to_registered_users',
        'do_not_display_to_anonymous_users',
        'labels',
        'disable', 'utm_campaign', 'utm_medium',
        'do_not_display_to_donating_users',
        'do_not_display_to_donating_users_days_ago',
        'display_to_paying_users',
        'do_not_display_to_paying_users',
        'targeting_countries',
        'targeting_cities',
        'targeting_invert',
    ]

    def get_queryset(self, request):
        qs = super(LineItemAdmin, self).get_queryset(request)
        active_views_subquery = Log.objects.filter(line_item=OuterRef('pk')).values('line_item').annotate(c=Count('id')).values('c')
        active_clicks_subquery = Log.objects.filter(line_item=OuterRef('pk'), clicked=True).values('line_item').annotate(c=Count('id')).values('c')
        return qs.annotate(
            active_views=Subquery(active_views_subquery, output_field=IntegerField()),
            active_clicks=Subquery(active_clicks_subquery, output_field=IntegerField())
        )

    def combined_views(self, obj):
        active_views = getattr(obj, 'active_views', None)
        if active_views is None:
            active_views = Log.objects.filter(line_item=obj).count()
        return obj.views + (active_views or 0)
    combined_views.short_description = 'Combined Views'

    def combined_clicks(self, obj):
        active_clicks = getattr(obj, 'active_clicks', None)
        if active_clicks is None:
            active_clicks = Log.objects.filter(line_item=obj, clicked=True).count()
        return obj.clicks + (active_clicks or 0)
    combined_clicks.short_description = 'Combined Clicks'


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    pass


@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    list_display = ['name', 'line_item', 'combined_views', 'combined_clicks', 'views', 'clicks']
    readonly_fields = ['combined_views', 'combined_clicks', 'views', 'clicks']
    fields = [
        'name', 'utm_campaign', 'utm_medium', 'utm_source',
        'image_click_through_url', 'image', 'image_url', 'html', 'iframe',
        'line_item', 'disable', 'combined_views', 'combined_clicks', 'views', 'clicks',
        'labels', 'fluid', 'priority'
    ]

    def get_queryset(self, request):
        qs = super(CreativeAdmin, self).get_queryset(request)
        active_views_subquery = Log.objects.filter(creative=OuterRef('pk')).values('creative').annotate(c=Count('id')).values('c')
        active_clicks_subquery = Log.objects.filter(creative=OuterRef('pk'), clicked=True).values('creative').annotate(c=Count('id')).values('c')
        return qs.annotate(
            active_views=Subquery(active_views_subquery, output_field=IntegerField()),
            active_clicks=Subquery(active_clicks_subquery, output_field=IntegerField())
        )

    def combined_views(self, obj):
        active_views = getattr(obj, 'active_views', None)
        if active_views is None:
            active_views = Log.objects.filter(creative=obj).count()
        return obj.views + (active_views or 0)
    combined_views.short_description = 'Combined Views'

    def combined_clicks(self, obj):
        active_clicks = getattr(obj, 'active_clicks', None)
        if active_clicks is None:
            active_clicks = Log.objects.filter(creative=obj, clicked=True).count()
        return obj.clicks + (active_clicks or 0)
    combined_clicks.short_description = 'Combined Clicks'

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
    log_objects = queryset.values(
        'user__username', 'ad_unit_placements',
        'line_item__name', 'datetime', 'clicked', 'creative_id',
        'ad_unit_name', 'ip', 'country', 'city',
        'capping_status_day', 'capping_status_week', 'capping_status_month'
    )
    creatives_pks = queryset.values_list('creative_id', flat=True).distinct()
    creatives_dict = {c.pk: c for c in Creative.objects.filter(pk__in=list(creatives_pks))}
    for log_object in log_objects:
        creative: Creative = creatives_dict[log_object["creative_id"]]
        if log_object['user__username'] is not None:
            username = log_object['user__username']
        else:
            username = ''
        if log_object['ad_unit_placements']:
            placements_str = ", ".join(log_object['ad_unit_placements'])
        else:
            placements_str = ''
        if log_object['line_item__name']:
            line_item_name = log_object['line_item__name']
        else:
            line_item_name = ''
        writer.writerow([
            log_object['datetime'].strftime("%Y-%m-%d %H:%M:%S.%f"),
            log_object['clicked'],
            line_item_name,
            creative.name,
            f'{creative.width}x{creative.height}',
            log_object['ad_unit_name'],
            placements_str,
            username,
            log_object['ip'] or '',
            log_object['country'] or '',
            log_object['city'] or '',
            log_object['capping_status_day'] or '',
            log_object['capping_status_week'] or '',
            log_object['capping_status_month'] or ''
        ])
    return response

export_csv.short_description = "Export CSV"


class ExcludeUserFilter(admin.SimpleListFilter):
    title = 'Exclude users'
    parameter_name = 'exclude_users'

    def lookups(self, request, model_admin):
        return (
            ('admins', 'Admins'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'admins':
            return queryset.exclude(Q(ip='94.188.74.123')|Q(user__is_superuser=True))
        else:
            return queryset


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
    list_filter = ['line_item', 'datetime', 'clicked', ExcludeUserFilter]
    readonly_fields = [field.name for field in Log._meta.fields]

    actions = [export_csv]
