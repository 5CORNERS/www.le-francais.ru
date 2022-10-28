import random
from typing import Dict, List

from dateutil.parser import isoparse
from django.db.models import F, Q
from django.http import JsonResponse, HttpResponseNotFound, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import RedirectView, TemplateView

from .consts import LOG_TYPE_VIEW
from .models import Creative, LineItem, Log
from .utils import clear_session_data


class AdCounterRedirectView(RedirectView):
    """
    ?utm_campaign=campaign&utm_medium=medium&utm_source=source
    """
    def get_redirect_url(self, *args, **kwargs):
        creative = get_object_or_404(Creative, pk=kwargs['creative'])
        line_item = get_object_or_404(LineItem, pk=kwargs['line_item'])
        utm_source = kwargs['source']

        if not self.request.user.is_staff:

            creative.clicks = F('clicks') + 1
            creative.save(update_fields=['clicks'])

            line_item.clicks = F('clicks') + 1
            line_item.save(update_fields=['clicks'])

        return creative.image_click_through_url \
               + f'?utm_campaign={creative.utm_campaign}&utm_medium={creative.utm_medium}&utm_source={utm_source}'


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
    try:
        max_width = float(request.GET.get('max_width'))
    except ValueError:
        max_width = 10000
    page_view_id = request.GET.get('page_view_id')
    now_isoformat = timezone.now().isoformat()
    line_items = LineItem.objects.all()
    if name:
        line_items = line_items.filter(
            Q(ad_units__contains=[name]) | Q(
                ad_units__len=0
            )
        )
    if placements:
        line_items = line_items.filter(
            Q(placements__code__in=placements) | Q(
                placements__isnull=True)
        )

    if request.user.is_authenticated:
        line_items = line_items.exclude(
            do_not_display_to_registered_users=True
        )

    if line_items.count() == 0:
        return {'empty': True}

    session = request.session
    was_on_pages = session.get('was_on_pages', {})
    was_on_conjugations = session.get('was_on_conjugations', False)

    if was_on_pages:
        line_items = line_items.exclude(
            do_not_show_to__contains=list(was_on_pages.keys())
        )
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
                    CAPPING_EMPTY
                )['times']]
            ),
            line_items_list
        ))

    creatives = Creative.objects.select_related('line_item').filter(
        line_item_id__in=[li.pk for li in line_items_list]
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
        used_labels[page_view_id] = LABELS_EMPTY
        used_labels[page_view_id]['datetime'] = now_isoformat

    if creatives_list:
        if sizes:
            chosen_creative = random.choice(creatives_list)
        else:
            creatives_list.sort(key=lambda c: c.width, reverse=True)
            max_chosen_width = creatives_list[0].width
            chosen_creative = random.choice([c for c in creatives_list if c.width == max_chosen_width])
        # TODO: choosing by random

        # storing labels
        chosen_labels = set(chosen_creative.labels) & set(
            chosen_creative.line_item.labels) if chosen_creative.labels is not None else None
        if chosen_labels:
            used_labels[page_view_id]['labels'] = list(
                set(used_labels[page_view_id]['labels']) & chosen_labels
            )
            used_labels[page_view_id]['datetime'] = now_isoformat
        session['ads_labels'] = used_labels

        # storing cappings
        try:
            line_item_capping = cappings[chosen_creative.line_item.name]
        except KeyError:
            line_item_capping = CAPPING_EMPTY
            line_item_capping['first_time'] = now_isoformat
        line_item_capping['last_time'] = now_isoformat
        line_item_capping['times'].append(now_isoformat)
        cappings[chosen_creative.line_item.name] = line_item_capping
        if not request.user.is_staff or 'test' in request.GET:
            session['ads_cappings'] = cappings

        clear_session_data(session)

        # count statistics
        if not request.user.is_staff:
            chosen_creative.views += 1
            chosen_creative.save(update_fields=['views'])
            chosen_creative.line_item.views += 1
            chosen_creative.line_item.save(update_fields=['views'])
        geoip_dict = request.session.get('geoip', None)
        if geoip_dict:
            country = geoip_dict['country_name']
            city = geoip_dict['city']
        else:
            country = None
            city = None
        Log.objects.create(
            log_type=LOG_TYPE_VIEW,
            creative=chosen_creative,
            line_item=chosen_creative.line_item,
            user=request.user if request.user.is_authenticated else None,
            ip=session.ip,
            country=country,
            city=city,
        )

        return {'empty': False,
                'body_html': chosen_creative.serve_body(request),
                'head_html': chosen_creative.serve_head(request),
                }
    else:
        return {'empty': True}

def get_creative(request):
    creative_dict = get_creative_dict(request)
    if creative_dict['empty']:
        return HttpResponseNotFound()
    else:
        return JsonResponse(data=creative_dict)


def image_redirect(request, uuid):
    creative = get_object_or_404(Creative, uuid=uuid)
    return HttpResponseRedirect(creative.get_image_url())

def image_click_through(request, uuid):
    creative = get_object_or_404(Creative, uuid=uuid)
    return HttpResponseRedirect(creative.image_click_through_url)
