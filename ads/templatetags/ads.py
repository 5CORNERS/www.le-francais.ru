import json
import re
from typing import List

import shortuuid
from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template
from django.db.models import Q, F, Count, Case, When, IntegerField
from django.template.base import token_kwargs
from django.template.defaulttags import register
from django.utils import timezone

from ads.models import LineItem, Creative
from home.models import InlineAdvertisementSnippet, PageLayoutAdvertisementSnippet


def parse_sizes_to_list(sizes) -> list:
    """
    (vgt: 960px) 540px, 100%
    vgt — viewport greater then

    [['v|c',[1200,0][[300,600][300,250][336,268]]], ...]
    """
    if isinstance(sizes, list):
        return sizes
    elif isinstance(sizes, str):
        try:
            return json.loads(sizes)
        except json.JSONDecodeError:
            return []
    pattern = re.compile(
        '(?:\((?P<type>\w{3}?):\s(?P<type_details>\d+px)\)\s)?(?P<width>\d+(?:px|%))x?(?P<height>\d+px)?')
    if not bool(sizes):
        sizes_str_list = []
    elif isinstance(sizes, str):
        sizes_str_list = sizes.split(', ')
    elif isinstance(sizes, list):
        sizes_str_list = sizes
    else:
        raise ValueError("'sizes' must be list or string")
    result = []
    for size_str in sizes_str_list:
        match = pattern.match(size_str)
        size_type = match.group('type')
        type_details = match.group('type_details')
        width = match.group('width')
        height = match.group('height')
        if '%' in width:
            fluid = True
            width = width.strip('%')
        else:
            fluid = False
            if 'px' in width:
                width = width.strip('px')
        if isinstance(width, str):
            width = int(width)
        if isinstance(height, str) and 'px' in height:
            height = int(height.strip('px'))
        result.append({'type': size_type or None,
                       'details': type_details or None,
                       'width': width, 'height': height,
                       'fluid': fluid})
    return result

def format_sizes_from_list(sizes_list) -> str:
    ...

def get_ads(context, ad_unit_name, ad_unit_placement_code, sizes_str,
            floating_image=None, utm_source=None, adsense=False):
    line_items = LineItem.objects.filter().order_by('-priority')
    if ad_unit_name:
        line_items = line_items.filter(
            Q(ad_units__contains=[ad_unit_name]) | Q(ad_units__len=0))
    if ad_unit_placement_code:
        line_items = line_items.filter(
            Q(placements__code=ad_unit_placement_code) | Q(
                placements__isnull=True))

    if context['request'].user.is_authenticated:
        line_items = line_items.exclude(
            do_not_display_to_registered_users=True)

    session = context['request'].session

    was_on_pages = session.get('was_on_pages', {})
    was_on_conjugations = session.get('was_on_conjugations', False)
    if was_on_pages:
        line_items = line_items.exclude(
            do_not_show_to__contains=list(was_on_pages.keys()))
    if was_on_conjugations:
        line_items = line_items.exclude(
            do_not_show_if_was_on_conjugations=True)

    if line_items.count() == 0:
        return {'empty': True, 'adsense': True}

    request_id = context['request'].request_id
    labels = session.get('ads_labels', {})
    if not isinstance(labels, dict):
        labels = {}

    labels = {
        'request_id': request_id,
        'used_labels': [],
    }
    if not labels or labels['request_id'] != request_id:
        labels = {
            'request_id': request_id,
            'used_labels': [],
        }
    else:
        line_items.exclude(
            labels__contains=labels['used_labels']).annotate(
            used_labels_creative_count=Count(
                Case(When(~Q(creative__labels__contained_by=labels[
                    'used_labels']), then=1),
                     output_field=IntegerField(),
                     )
            )
        ).filter(
            used_labels_creative_count=0
        )

    if not context['request'].user.is_staff:
        cappings = session.get('ads_cappings', {})
        if not isinstance(cappings, dict):
            cappings = {}

        for line_item in line_items:
            if not line_item.name in cappings:
                break
            elif line_item.check_cappings(
                    cappings[line_item.name]['times']):
                break
            else:
                return {'empty': True, 'adsense': True}

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
    else:
        line_item = line_items.first()

    if line_item.labels:
        labels['used_labels'] = labels[
                                    'used_labels'] + line_item.labels

    creatives: List[Creative] = list(
        line_item.creatives.filter(disable=False))

    creatives_list = []
    for creative in creatives:
        creatives_list.append({
            'image_url': creative.get_image_url(),
            'image_click_through_url': creative.get_click_through_url(
                line_item, utm_source),
            'width': creative.width,
            'height': creative.height,
            'labels': creative.labels
        })

    if sizes_str:
        sizes_list = parse_sizes_to_list(sizes_str)
    else:
        sizes_list = None

    if not context['request'].user.is_staff:
        line_item.views = F('views') + 1
        line_item.save()

    return {'empty': False, 'adsense': adsense,
            'creatives': creatives_list, 'line_item': line_item,
            'sizes_str': sizes_str,
            'sizes': sizes_list,
            'creatives_list_json': json.dumps(creatives_list),
            'id': shortuuid.uuid(),
            'sizes_list_json': json.dumps(sizes_list),
            'floating_image': floating_image}


VAR_NAMES = [
    'ad_unit_name', 'ad_unit_placement_code', 'sizes_str',
    'floating_image', 'utm_source', 'adsense'
]


@register.inclusion_tag('ads/include_ad.html')
def include_ad(ad_unit_name, ad_unit_placement_codes,
               sizes_str=None,
               floating_image=False, utm_source=None,
               adsense=False, adsense_page_type=None,
               adsense_placement=None,
               adsense_inline_adunit_name=None,
               adsense_in_house=None,
               wo_script=False):
    if sizes_str is not None:
        sizes_list = parse_sizes_to_list(sizes_str)
    else:
        sizes_list = []
    try:
        ad_unit_placement_codes = json.dumps(ad_unit_placement_codes.split('|'))
    except:
        ad_unit_placement_codes = []

    return {
        'ad_unit_placement_codes': ad_unit_placement_codes,
        'ad_unit_name': ad_unit_name,
        'sizes_list': json.dumps(sizes_list),
        'floating_image': floating_image, 'ad_unit_utm_source': utm_source,
        'adsense': adsense, 'id': shortuuid.uuid(),
        'wo_script':wo_script
    }


@register.tag
def with_adsense():
    """"""

class IncludeAd(InclusionTag):
    push_context = True
    template = 'ads/include_ad.html'
    name = 'include_ad'
    options = Options(
        Argument('ad_unit_name', required=True),
        Argument('ad_unit_placement_code', required=True),
        Argument('sizes_str', None, required=False),
        Argument('floating_image', False, required=False),
        Argument('utm_source', None, required=False),
        Argument('adsense', False, required=False),
        blocks=[('with_adsense', 'adsense_nodelist')]
    )

    def __init__(self, *args, **kwargs):
        super(IncludeAd, self).__init__(*args, **kwargs)
        self.adsense = False

    def get_context(self, context, **kwargs):
        ad_kwargs = dict(kwargs)
        del ad_kwargs['adsense_nodelist']
        ad_context = get_ads(context, **ad_kwargs)
        if ad_context['empty'] and ad_context['adsense']:
            self.adsense = True
        return {**context, **ad_context}

    def render_tag(self, context, **kwargs):
        ad_output = super(IncludeAd, self).render_tag(context,
                                                      **kwargs)
        if not self.adsense:
            return ad_output
        else:
            return self.adsense_nodelist.render(context)


# register.tag(IncludeAd)


class IncludeAdNode(template.Node):
    def __init__(self, fill_content, ):
        """
        :type fill_content: django.template.base.NodeList
        """

    def render(self, context):
        return ''
