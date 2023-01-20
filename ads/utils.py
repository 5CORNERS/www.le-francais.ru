import dateutil.parser
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


def parse_capping_times(times):
    parsed_times = []
    for time in times:
        parsed_times.append(
            dateutil.parser.isoparse(time) if isinstance(time,
                                                         str) else time)
    return parsed_times


def calculate_times(times, now=None):
    if now is None:
        now = timezone.now()
    in_day = 0
    in_week = 0
    in_month = 0
    for time in times:
        if isinstance(time, str):
            time = isoparse(time)
        delta = now - time
        if delta.days < 30:
            in_month += 1
        if delta.days < 7:
            in_week += 1
        if delta.days < 1:
            in_day += 1
    return in_day, in_week, in_month
