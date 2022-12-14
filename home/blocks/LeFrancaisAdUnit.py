from wagtail.core import blocks

from ads.utils import parsed_media_query_to_str


def get_placements():
    from ads.models import Placement
    return [(placement.code, placement.name) for placement in Placement.objects.all()]

class AdUnitSizeBlock(blocks.StructBlock):
    type = blocks.ChoiceBlock(choices=[
        ('vgt', 'viewport size greater than'),
        ('vlt', 'viewport size less than'),
        ('cgt', 'parent container size greater than or equal'),
        ('clt', 'parent container size less than or equal'),
    ], required=False)
    window_or_container_size = blocks.CharBlock(required=False, help_text='320px')
    ad_unit_size = blocks.CharBlock(required=True, help_text='250px, 100%, ...')


class SimpleSizeBlock(blocks.StructBlock):
    width = blocks.IntegerBlock()
    width_percents = blocks.BooleanBlock(required=False, )
    height = blocks.IntegerBlock()

class AdUnitSizeBlockAdvanced(blocks.StructBlock):
    type = blocks.ChoiceBlock(choices=[
        ('v', 'viewport size greater than'),
        ('c', 'parent container size greater than or equal'),
    ], required=False)
    window_or_container_size = blocks.CharBlock(required=False, help_text='320x0 (width greater or equal than 320 and height greater or equal then 0)')
    sizes = blocks.ListBlock(SimpleSizeBlock)


class LeFrancaisAdUnitBlock(blocks.StructBlock):
    ad_unit_name = blocks.CharBlock()
    placements = blocks.ListBlock(blocks.ChoiceBlock(choices=get_placements()), required=False, default=[])
    utm_source = blocks.CharBlock()
    floating_image = blocks.ChoiceBlock(choices=[
        ('left', 'Left'), ('center', 'Center'), ('right', 'Right')
    ], required=False, help_text='TODO')
    sizes = blocks.ListBlock(AdUnitSizeBlockAdvanced)

    def get_context(self, value, parent_context=None):
        context = super(LeFrancaisAdUnitBlock, self).get_context(value,
                                                           parent_context=None)
        context = {**context, **parent_context}
        media_query = []

        value['sizes'] = sizes_json(value['sizes'])

        context['media_query'] = parsed_media_query_to_str(media_query)
        context['floating_image'] = None

        value['adsense'] = True
        value['adsense_page_type'] = None
        value['adsense_placement'] = None
        value['adsense_inline_adunit_name'] = None
        value['adsense_in_house'] = None
        value['placements'] = '|'.join([p for p in value['placements'] if p is not None])


        return context

    class Meta:
        icon = 'image'
        template = 'blocks/le_francais_ad_unit.html'


def sizes_json(sizes):
    if not sizes:
        return None
    result = []
    for size in sizes:
        part_1 = []
        if size['type']:
            part_1.append(size['type'])
        else:
            part_1.append('v')
        part_1.append(size['window_or_container_size'].split('x'))
        part_2 = []
        for simple_size in size['sizes']:
            w, h , w_p = simple_size.get('width'), simple_size.get('height'), simple_size.get('width_percents')
            if w is not None and h is not None:
                part_2.append([w, h, w_p])
        result.append([part_1, part_2])
    return result
