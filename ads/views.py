import random
from typing import Dict, List

from dateutil.parser import isoparse
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Q, Count, Func
from django.http import JsonResponse, HttpResponseNotFound, \
    HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import RedirectView, TemplateView

from .consts import LOG_TYPE_VIEW, LOG_TYPE_CLICK
from .models import Creative, LineItem, Log
from .utils import clear_session_data, calculate_times


class AdCounterRedirectView(RedirectView):
    """
    ?utm_campaign=campaign&utm_medium=medium&utm_source=source
    """
    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        creative = get_object_or_404(Creative, uuid=kwargs['uuid'])
        line_item = creative.line_item
        utm_campaign = creative.utm_campaign or creative.line_item.utm_campaign
        if utm_campaign is not None:
            utm_campaign = f"utm_campaign={utm_campaign}"
        utm_medium = creative.utm_medium or creative.line_item.utm_medium
        if utm_medium is not None:
            utm_medium = f"utm_medium={utm_medium}"
        if 'utm_source' in kwargs:
            utm_source = f"utm_source={kwargs['utm_source']}"
        else:
            utm_source = None
        #
        # if creative.utm_source is not None:
        #     utm_source = f"utm_source={creative.utm_source}"

        if not user.is_staff:

            creative.clicks = F('clicks') + 1
            creative.save(update_fields=['clicks'])

            line_item.clicks = F('clicks') + 1
            line_item.save(update_fields=['clicks'])

        log_id = kwargs.get('log_id', None)
        if log_id is not None:
            try:
                log_object = Log.objects.get(pk=log_id)
                log_object.clicked = True
                log_object.click_datetime = timezone.now()
                log_object.save(update_fields=['clicked', 'click_datetime'])
            except Log.DoesNotExist:
                pass

        get_args = [utm_campaign, utm_medium, utm_source]
        get_string = "?" + "&".join([a for a in get_args if a is not None])
        url = creative.image_click_through_url
        if not url:
            url = "https://example.com"
        return url + get_string


class TestView(TemplateView):
    template_name = 'ads/test.html'

CAPPING_EMPTY = {
    'first_time': None,
    'last_time': None,
    'times': []
}
LABELS_EMPTY = {
    'labels': [],
    'datetime': None
}

def get_creative_dict(request) -> Dict:
    name = request.GET.get('ad_unit_name')
    placements = request.GET.getlist('placement')
    sizes = request.GET.getlist('sizes')
    country_code = request.session['geoip'].get('country_code')
    city = request.session['geoip'].get('city')
    utm_source = request.GET.get('ad_unit_utm_source')
    try:
        max_width = float(request.GET.get('max_width'))
    except ValueError:
        max_width = 10000
    page_view_id = request.GET.get('page_view_id')
    now = timezone.now()
    now_isoformat = now.isoformat()
    line_items = LineItem.objects.filter(disable=False).order_by('-priority')

    # line_items = line_items.filter(
    #     Q(targeting_country__isnull=True) | Q(targeting_country__contains=[country_code], targeting_invert=False)
    # ).exclude(
    #     targeting_country__contains=[country_code], targeting_invert=True
    # ).filter(
    #     Q(targeting_city__isnull=True) | Q(targeting_city__contains=[city], targeting_invert=False)
    # ).exclude(
    #     targeting_city__contains=[country_code], targeting_invert=True
    # )

    if country_code is not None:
        line_items = line_items.exclude(targeting_countries__contains=[country_code], targeting_invert=True).filter(
            Q(targeting_invert=True) | Q(targeting_countries__contains=[country_code]) | Q(targeting_countries__len=0)
        )
    else:
        line_items = line_items.filter(targeting_countries__len=0)
    if city is not None:
        line_items = line_items.exclude(targeting_cities__contains=[city], targeting_invert=True).filter(
            Q(targeting_invert=True) | Q(targeting_cities__contains=[city]) | Q(targeting_cities__len=0)
        )
    else:
        line_items = line_items.filter(targeting_cities__len=0)

    if name:
        line_items = line_items.filter(
            Q(ad_units__contains=[name]) | Q(
                ad_units__len=0
            )
        )
    else:
        line_items = line_items.filter(
            ad_units__len=0
        )
    if placements:
        # line_items = line_items.exclude(placements__code__in=[placements], placements_inverted=True).filter(
        #     Q(placements__code__in=[placements], placements_inverted=False) | Q(placements__isnull=True, placements_inverted=False)
        # )
        line_items = line_items.exclude(placements__code__in=placements, placements_inverted=True)
        line_items = line_items.filter(Q(placements_inverted=True) | Q(placements__code__in=placements, placements_inverted=False) | Q(placements__isnull=True))

        line_items = line_items.annotate(placements_and_arr=ArrayAgg('placements_and')).annotate(placements_and_len=Func(F('placements_and_arr'), function='CARDINALITY')).exclude(placements_and_arr__contains=placements, placements_and_len=len(placements))
        line_items = line_items.filter(Q(placements_and_inverted=True) | Q(
            placements_and_arr__contains=placements, placements_and_inverted=False, placements_and_len=len(placements)
        ) | Q(placements_and__isnull=True))

    if request.user.is_authenticated:
        line_items = line_items.exclude(
            do_not_display_to_registered_users=True
        )

        if request.user.donation_set.filter(cancelled=False).exists():
            last_donation_days_ago = (
                        timezone.now() - request.user.donation_set.filter(
                    cancelled=False).order_by(
                    "datetime_creation").last().datetime_creation).days
            line_items = line_items.exclude(
                Q(do_not_display_to_donating_users=True
                  ) | Q(
                    do_not_display_to_donating_users_days_ago__gt=last_donation_days_ago))

        if request.user.has_payed():
            line_items = line_items.exclude(
                do_not_display_to_paying_users=True
            )
        else:
            line_items = line_items.exclude(
                display_to_paying_users=True
            )

    if request.user.is_anonymous:
        line_items = line_items.exclude(
            do_not_display_to_anonymous_users=True
        )

    if line_items.count() == 0:
        return {'empty': True, 'country_code': country_code, 'city': city,
                'name': name, 'placements': placements,
                'is_authenticated': request.user.is_authenticated}

    session = request.session
    was_on_pages:dict = session.get('was_on_pages', {})
    was_on_conjugations = session.get('was_on_conjugations', False)

    if was_on_pages:
        for page, data in was_on_pages.items():
            last_time = isoparse(data['last_time'] or data['first_time'])
            days_ago = (timezone.now() - last_time).days

            line_items = line_items.exclude(
                less_than_n_days_ago=True, less_than_n_days_ago_value__gt=days_ago, do_not_show_to__contains=[page]
            ).exclude(less_than_n_days_ago=False, do_not_show_to__contains=[page])

    if was_on_conjugations:
        line_items = line_items.exclude(
            do_not_show_if_was_on_conjugations=True)

    line_items_list:List[LineItem] = list(line_items)

    # cappings filtering
    cappings = session.get('ads_cappings', {})
    if request.user.is_staff:
        pass
    else:
        line_items_list = list(filter(
            lambda li: li.check_cappings(
                [isoparse(t) for t in cappings.get(
                    li.name,
                    {
                        'first_time': None,
                        'last_time': None,
                        'times': []
                    }
                )['times']]
            ),
            line_items_list
        ))

    creatives = Creative.objects.select_related('line_item').filter(
        line_item_id__in=[li.pk for li in line_items_list], disable=False
    ).order_by('-line_item__priority')

    fixed_width_sizes = []
    fluid_sizes = []
    for size in sizes:
        size_str, fluid = size.split(':')
        fluid = fluid == 'true'
        width, height = size_str.split('x')
        width = int(width) if width != 'null' else None
        height = int(height) if height != 'null' else None
        if not fluid and width is not None:
            fixed_width_sizes.append(
                {'width': width, 'height': height, 'fluid': fluid})
        else:
            fluid_sizes.append(
                {'width': width, 'height': height, 'fluid': fluid})

    fixed_width_sizes = list(filter(lambda x: x['width'] <= max_width, fixed_width_sizes))
    fixed_width_sizes.sort(key=lambda x: x['width'], reverse=True)

    sizes = fluid_sizes + fixed_width_sizes

    if sizes:
        creatives_list = list(filter(
            lambda c: (((c.width, c.height) in [(s['width'], s['height']) for s in sizes]) or (c.fluid and [s['fluid'] for s in sizes])) and (c.width < max_width),
            creatives
        ))
    else:
        creatives_list = list(filter(
            lambda c: (c.width < max_width),
            creatives
        ))

    # labels filtering
    used_labels: dict = session.get('ads_labels', {})
    if page_view_id in used_labels.keys():
        labels = used_labels[page_view_id]['labels']
        creatives_list = list(filter(
            lambda x: not (set(x.labels) & set(labels)
                           or set(x.line_item.labels) & set(labels)),
        creatives_list
        ))
    else:
        used_labels[page_view_id] = {
            'labels': [],
            'datetime': None
        }
        used_labels[page_view_id]['datetime'] = now_isoformat

    if creatives_list:

        chosen_line_items = list(set(c.line_item for c in creatives_list))
        chosen_line_items.sort(key=lambda l: l.priority, reverse=True)
        if len(chosen_line_items) > 1:
            chosen_line_item = chosen_line_items[0]
            creatives_list = [c for c in creatives_list if c.line_item_id == chosen_line_item.pk]

        if sizes:
            pass
        else:
            creatives_list.sort(key=lambda c: c.width, reverse=True)
            max_chosen_width = creatives_list[0].width
            creatives_list = [c for c in creatives_list if c.width == max_chosen_width or c.fluid]

        max_creative_priority = max(c.priority for c in creatives_list)
        creatives_with_max_priority = [c for c in creatives_list if c.priority==max_creative_priority]
        chosen_creative: Creative = random.choice(creatives_with_max_priority)
        # TODO: choosing by random

        # storing labels
        chosen_labels = set(chosen_creative.labels) | set(
            chosen_creative.line_item.labels)
        if chosen_labels:
            used_labels[page_view_id]['labels'] = list(
                set(used_labels[page_view_id]['labels']) | chosen_labels
            )
            used_labels[page_view_id]['datetime'] = now_isoformat
        session['ads_labels'] = used_labels

        # storing cappings
        try:
            line_item_capping = cappings[chosen_creative.line_item.name]
        except KeyError:
            line_item_capping = {'first_time': now_isoformat,
                                 'last_time': None,
                                 'times': []
                                 }
        line_item_capping['last_time'] = now_isoformat
        line_item_capping['times'].append(now_isoformat)
        cappings[chosen_creative.line_item.name] = line_item_capping
        cappings_day, cappings_week, cappings_month = calculate_times(line_item_capping['times'], now)
        if not request.user.is_staff or 'test' in request.GET:
            session['ads_cappings'] = cappings

        clear_session_data(session)
        request.session = session

        # count statistics
        if not request.user.is_staff:
            chosen_creative.views += 1
            chosen_creative.save(update_fields=['views'])
            chosen_creative.line_item.views += 1
            chosen_creative.line_item.save(update_fields=['views'])
        geoip_dict = request.session.get('geoip', None)
        if geoip_dict:
            country = geoip_dict.get('country_name')
            city = geoip_dict.get('city')
        else:
            country = None
            city = None
        log_object = Log.objects.create(
            log_type=LOG_TYPE_VIEW,
            creative=chosen_creative,
            line_item=chosen_creative.line_item,
            user=request.user if request.user.is_authenticated else None,
            ip=session.ip,
            country=country,
            city=city,
            ad_unit_name=name,
            ad_unit_placements=placements,
            utm_data={
                "utm_campaign": chosen_creative.utm_campaign or chosen_creative.line_item.utm_campaign,
                "utm_medium": chosen_creative.utm_medium or chosen_creative.line_item.utm_medium,
                "utm_source": chosen_creative.utm_source or utm_source
            },
            capping_status_day=cappings_day,
            capping_status_week=cappings_week,
            capping_status_month=cappings_month
        )

        return {'empty': False,
                'body_html': chosen_creative.serve_body(request, utm_source, log_object.pk),
                'head_html': chosen_creative.serve_head(request, sizes),
                'utm_source': utm_source, 'log_id': log_object.pk
                }
    else:
        return {
            'empty': True, 'was_on_pages': was_on_pages, 'was_on_conjugations': was_on_conjugations,
            'cappings': cappings, 'sizes': sizes, 'used_labels': used_labels, 'page_view_id': page_view_id
        }

def get_creative(request):
    creative_dict = get_creative_dict(request)
    if creative_dict['empty']:
        return JsonResponse(data=creative_dict, status=404)
    else:
        return JsonResponse(data=creative_dict)


def image_redirect(request, uuid):
    creative = get_object_or_404(Creative, uuid=uuid)
    return HttpResponseRedirect(creative.get_image_url())

def image_click_through(request, uuid):
    creative = get_object_or_404(Creative, uuid=uuid)
    return HttpResponseRedirect(creative.image_click_through_url)


def creative_get_iframe(request, uuid, log_id):
    creative = get_object_or_404(Creative, uuid=uuid)
    html = creative.get_iframe_content(int(log_id))
    return HttpResponse(html, content_type='text/html')
