from dateutil.parser import isoparse
from django.utils import timezone


def parsed_media_query_to_str(media_query:list) -> str:
    """
    [
    ('wgt', '800px', '320px'),
    ('vlt', '321px', '100%'),
    (None, None, '1px')
    ]
    """
    result = ''
    for type_name, type_details, size in media_query:
        if type_name is not None and type_name != '':
            result += f'({type_name}: {type_details}) {size}, '
        else:
            result += f'{size}, '
    return result[:-2]

LABELS_DAYS_LIMIT = 1
CAPPINGS_DAYS_LIMIT = 31

def clear_session_data(session):
    # clear labels
    ads_labels = session.get('ads_labels', {})
    for page_view_id, labels_data in list(ads_labels.items()):
        if labels_data['datetime'] is None or (timezone.now() - isoparse(labels_data['datetime'])).days > 1:
            del session['ads_labels'][page_view_id]

    # clear cappings
    ads_cappings = session.get('ads_cappings', {})
    for line_item_name, cappings_data in list(ads_cappings.items()):
        for i, time in reversed(list(enumerate(cappings_data['times']))):
            if (timezone.now() - isoparse(time)).days > CAPPINGS_DAYS_LIMIT:
                del cappings_data['times'][i]
        if len(cappings_data['times']) == 0:
            del session['ads_cappings'][line_item_name]
