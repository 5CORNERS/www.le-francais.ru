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

class LeFrancaisAdUnitBlock(blocks.StructBlock):
    ad_unit_name = blocks.CharBlock()
    placement = blocks.ChoiceBlock(choices=get_placements(), required=False)
    floating_image = blocks.ChoiceBlock(choices=[
        ('left', 'Left'), ('center', 'Center'), ('right', 'Right')
    ], required=False, help_text='TODO')
    sizes = blocks.ListBlock(AdUnitSizeBlock)

    def get_context(self, value, parent_context=None):
        context = super(LeFrancaisAdUnitBlock, self).get_context(value,
                                                           parent_context=None)
        context = {**context, **parent_context}
        media_query = []
        for size in value['sizes']:
            media_query.append((
                size['type'],
                size['window_or_container_size'],
                size['ad_unit_size']
            ))

        context['media_query'] = parsed_media_query_to_str(media_query)
        return context

    class Meta:
        icon = 'image'
        template = 'blocks/le_francais_ad_unit.html'
