import json
import socket
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


class MetricsFormatter(logging.Formatter):

    def __init__(self, default_extra=None, fqdn=False):
        super().__init__()
        self.default_extra = default_extra or {}
        # if fqdn:
        #     self.host = socket.getfqdn()
        # else:
        #     self.host = socket.gethostname()

    def _format_timestamp(self, time):
        return (datetime.datetime.utcfromtimestamp(time)
                .strftime("%Y-%m-%dT%H:%M:%SZ"))

    def _get_extra(self, record):
        for key, value in record.__dict__.items():
            if key not in _SKIP_ATTRS:
                if isinstance(value, _SIMPLE_TYPES):
                    yield key, value
                else:
                    yield key, repr(value)

    def format(self, record):
        message = {
            '@timestamp': self._format_timestamp(record.created),
            '@version': '1',
            # 'host': self.host,
            # 'type': 'metricslog',
        }

        # add default extra fields
        message.update(self.default_extra)

        # add extra fields
        message.update(self._get_extra(record))
        return json.dumps(message)
