import datetime


def convert_timestamp_ms_to_time(timestamp_ms):
    timestamp_s = timestamp_ms / 1000.0

    # Convert to datetime
    dt_object = datetime.datetime.fromtimestamp(timestamp_s)

    return dt_object
