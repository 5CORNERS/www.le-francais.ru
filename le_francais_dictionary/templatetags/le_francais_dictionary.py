from django import template

register = template.Library()


@register.inclusion_tag('dictionary/dictionary.html')
def include_dictionary(lesson_page=None):
    """
    :type lesson_page: home.models.LessonPage
    """
    if lesson_page:
        return {'lesson_page': lesson_page}

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
