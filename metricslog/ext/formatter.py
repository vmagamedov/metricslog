import json
import logging
import datetime


_SKIP_ATTRS = {
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
    'processName', 'relativeCreated', 'thread', 'threadName', 'extra',
    'stack_info',
}

_SIMPLE_TYPES = (str, bool, dict, float, int, list, type(None))


def _json_value(value):
    return value if isinstance(value, _SIMPLE_TYPES) else str(value)


def _datetime_from_timestamp(timestamp):
    return (datetime.datetime.utcfromtimestamp(timestamp)
            .strftime('%Y-%m-%dT%H:%M:%S.000Z'))


def _datetime_from_timestamp_msec(timestamp):
    return (datetime.datetime.utcfromtimestamp(timestamp)
            .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')


class LogstashFormatter(logging.Formatter):

    def __init__(self, mapping=None, default_extra=None, msec=False):
        super().__init__()
        self.mapping = mapping or {}
        self.default_extra = default_extra or {}
        if msec:
            self._timestamp_format = _datetime_from_timestamp_msec
        else:
            self._timestamp_format = _datetime_from_timestamp

    def _get_extra(self, record):
        for key, value in record.__dict__.items():
            if key in self.mapping:
                yield self.mapping[key], _json_value(value)
            elif key not in _SKIP_ATTRS:
                yield key, _json_value(value)

    def format(self, record):
        message = {
            '@timestamp': self._timestamp_format(record.created),
            '@version': '1',
        }

        # add default extra fields
        message.update(self.default_extra)

        # add extra fields
        message.update(self._get_extra(record))
        return json.dumps(message)


class CEELogstashFormatter(LogstashFormatter):

    def __init__(self, app_name, mapping=None, default_extra=None, msec=False):
        super().__init__(mapping=mapping, default_extra=default_extra,
                         msec=msec)
        self.app_name = app_name

    def format(self, record):
        return '{}: @cee: '.format(self.app_name) + super().format(record)
