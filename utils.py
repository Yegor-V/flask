from datetime import datetime, timezone


def to_timestamp(date_string):
    dt = datetime.strptime(date_string, '%m/%d/%Y')
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def get_object_dict(table_row_object):
    table_row_dict = table_row_object.__dict__
    del table_row_dict['_sa_instance_state']
    return table_row_dict
