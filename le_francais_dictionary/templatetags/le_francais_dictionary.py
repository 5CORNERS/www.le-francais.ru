from django import template

from le_francais_dictionary.consts import TENSE_CHOICES, TYPE_CHOICES
from le_francais_dictionary.models import UserPacket

register = template.Library()


@register.inclusion_tag('dictionary/dictionary_tab.html', takes_context=True)
def include_dictionary(context, lesson_page):
    """
    :type lesson_page: home.models.LessonPage
    """
    return {'page': lesson_page,
            'hide_info': context['request'].COOKIES.get(
                'hide_flash_cards_info', None),
            'user': context['request'].user, 'request':context['request']}


@register.inclusion_tag('dictionary/dictionary_tab.html', takes_context=True)
def include_podcast_dictionary(context, podcast_page):
    """
    :type podcast_page: home.models.PodcastPage
    """
    return {

    }

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
def get_packets(context, page):
    """
    :type page: home.models.LessonPage
    """
    packets = page.get_word_packets()
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

@register.inclusion_tag('dictionary/tags/rating2stars.html')
def rating2stars(rating):
    if rating is None:
        return {'stars': None}
    rating = round(rating * 2) / 2
    integer, decimal  = divmod(rating, 1)
    stars = []
    for i in range(int(integer)):
        stars.append('full')
    if decimal:
        stars.append('half')
    for i in range(5 - len(stars)):
        stars.append('hollow')
    return {'rating': rating, 'stars': stars}

@register.inclusion_tag('dictionary/tags/repetitions2bars.html')
def repetitions2bars(count):
    return {'count':count}


@register.filter
def tense_name(t):
    return dict(TENSE_CHOICES).get(t, 'Unknown tense')

@register.filter
def type_name(t):
    return dict(TYPE_CHOICES).get(t, 'Unknown type')

@register.simple_tag
def iframe_height(c):
    if isinstance(c, int):
        if c > 50:
            c = 50
        return c * 30 + 116
    else:
        return 1616
