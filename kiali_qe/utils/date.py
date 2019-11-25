from datetime import datetime
from dateutil.tz import tzutc

REST_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

UI_FORMAT = '%b %d, %I:%M %p'


def parse_from_ui(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        # TODO: SWSQE-989
        return datetime.strptime(date_str, UI_FORMAT).\
            replace(year=datetime.now().year, tzinfo=tzutc())


def parse_from_rest(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        # TODO: SWSQE-989
        return datetime.strptime(date_str, REST_FORMAT).replace(second=0, tzinfo=tzutc())


def from_rest_to_ui(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        return parse_from_rest(date_str).strftime(UI_FORMAT)
