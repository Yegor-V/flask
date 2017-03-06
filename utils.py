from datetime import datetime, timezone


def to_timestamp(date_string):
    dt = datetime.strptime(date_string, '%m/%d/%Y')
    return int(dt.replace(tzinfo=timezone.utc).timestamp())
