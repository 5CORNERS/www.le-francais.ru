import json
import re
from typing import List

import shortuuid
from django.db.models import Q, F
from django.template.defaulttags import register
from django.utils import timezone

from ads.models import LineItem, Creative

def parse_sizes_to_list(sizes_str):
    """(vgt: 960px) 540px, 100%"""
    pattern = re.compile('(?:\((?P<type>\w{3}?):\s(?P<type_details>\d+px)\)\s)?(?P<size>\d+(?:px|%))')
    sizes_str_list = sizes_str.split(', ')
    result = []
    for size_str in sizes_str_list:
        match = pattern.match(size_str)
        type = match.group('type')
        type_details = match.group('type_details')
        size = match.group('size')
        result.append({'type': type or None, 'type_details': type_details or None, 'size': size})
    return result

@register.inclusion_tag('ads/include_ad.html', takes_context=True)
def include_ad(context, ad_unit_name, ad_unit_placement_code, sizes_str, floating_image=None):
    line_items = LineItem.objects.filter().order_by('-priority')
    if ad_unit_name:
        line_items = line_items.filter(Q(ad_units__contains=[ad_unit_name]) | Q(ad_units__len=0))
    if ad_unit_placement_code:
        line_items = line_items.filter(Q(placements__code=ad_unit_placement_code) | Q(placements__isnull=True))

    session = context['request'].session

    was_on_pages = session.get('was_on_pages', {})
    if was_on_pages:
        line_items = line_items.exclude(do_not_show_to__contains=list(was_on_pages.keys()))

    if line_items.count() == 0:
        return {'empty': True}

    cappings = session.get('ads_cappings', {})
    if not isinstance(cappings, dict):
        cappings = {}

    for line_item in line_items:
        if not line_item.name in cappings:
            break
        elif line_item.check_cappings(cappings[line_item.name]['times']):
            break
        else:
            return {'empty': True}

    now = timezone.now().isoformat()
    if not line_item.name in cappings:
        cappings[line_item.name] = {
            'first_time': now,
            'last_time': None,
            'times': [now]
        }
    else:
        cappings[line_item.name]['last_time'] = now
        cappings[line_item.name]['times'].append(now)
    session['ads_cappings'] = cappings

    creatives: List[Creative] = list(line_item.creatives.filter(disable=False))

    creatives_list = []
    for creative in creatives:
        creatives_list.append({
            'image_url': creative.get_image_url(),
            'click_through_url': creative.get_click_through_url(line_item),
            'width': creative.width,
            'height': creative.height,
        })

    sizes_list = parse_sizes_to_list(sizes_str)

    if not context['request'].user.is_staff:
        line_item.views = F('views') + 1
        line_item.save()

    return {'empty': False, 'creatives': creatives_list, 'line_item': line_item, 'sizes_str': sizes_str,
            'sizes': sizes_list, 'creatives_list_json': json.dumps(creatives_list),
            'id': shortuuid.uuid(), 'sizes_list_json': json.dumps(sizes_list), 'floating_image': floating_image}
