from datetime import datetime
from dateutil.tz import tzlocal, tzutc

REST_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

UI_FORMAT = '%m/%d/%Y, %I:%M:%S %p'


def parse_from_ui(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        return datetime.strptime(date_str, UI_FORMAT).replace(tzinfo=tzlocal()).astimezone(tzutc())


def parse_from_rest(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        return datetime.strptime(date_str, REST_FORMAT).replace(tzinfo=tzutc())


def from_rest_to_ui(date_str):
    if (date_str == '-') or (date_str == ''):
        return None
    else:
        return parse_from_rest(date_str).astimezone(tzlocal()).strftime(UI_FORMAT)
