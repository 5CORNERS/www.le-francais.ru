from django import template

from le_francais_dictionary.models import UserPacket

register = template.Library()


@register.inclusion_tag('dictionary/dictionary_tab.html', takes_context=True)
def include_dictionary(context, lesson_page):
    """
    :type lesson_page: home.models.LessonPage
    """
    return {'lesson_page': lesson_page,
            'hide_info': context['request'].COOKIES.get(
                'hide_flash_cards_info', None),
            'user': context['request'].user, 'request':context['request']}

@register.assignment_tag()
def get_packet_id(lesson_page):
    """
    :type lesson_page: home.models.LessonPage
    """
    try:
        packet = lesson_page.dictionary_packets.order_by('id').first()
    except:
        return None
    return packet.id

@register.assignment_tag(takes_context=True)
def get_packets(context, lesson_page):
    """
    :type context:
    :type lesson_page: home.models.LessonPage
    """
    packets = lesson_page.get_word_packets()
    # FIXME: remove adding packets
    if context.request.user.is_authenticated:
        for packet in packets:
            userpacker, created = UserPacket.objects.get_or_create(packet=packet, user=context.request.user)
    if packets.__len__() > 1:
        return packets
    elif not packets:
        return None
    else:
        return packets[0]
