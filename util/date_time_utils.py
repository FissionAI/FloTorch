from datetime import datetime, timezone


class DateTimeUtils:
    @staticmethod
    def parse_datetime(datetime_str):
        if not datetime_str:
            return None
        try:
            dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
