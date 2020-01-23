from datetime import datetime
from dateutil.tz import tzlocal, tzutc

REST_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

UI_FORMAT = '%b %d, %I:%M %p'


def parse_from_rest(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        return datetime.strptime(date_str, REST_FORMAT)


def from_rest_to_ui(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        date_texts = parse_from_rest(date_str).replace(
            second=0,
            tzinfo=tzutc()).astimezone(tzlocal()).strftime(UI_FORMAT).split(',')
        return '{},{}'.format(date_texts[0].lstrip("0").replace(" 0", " "), date_texts[1])
