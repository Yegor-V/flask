from datetime import datetime, timezone


def to_timestamp(date_string):
    if date_string == '':
        return None
    try:
        dt = datetime.strptime(date_string, '%m/%d/%Y')
    except ValueError:
        return 0
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def from_timestamp(timestamp):
    timestamp = int(timestamp)
    return datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%Y')
