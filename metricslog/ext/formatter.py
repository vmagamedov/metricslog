import json
import logging
import datetime
import traceback

from operator import itemgetter
from functools import partial

from ._colors import DEFAULT_FMT, DEFAULT_STYLES, PROC_MAP, CODES, NO_CODES


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
        record.message = record.getMessage()

        message = {
            '@timestamp': self._timestamp_format(record.created),
            '@version': '1',
        }

        # add default extra fields
        message.update(self.default_extra)

        # add extra fields
        message.update(self._get_extra(record))

        # TODO: add exception info

        return json.dumps(message)


class CEELogstashFormatter(LogstashFormatter):

    def __init__(self, app_name, mapping=None, default_extra=None, msec=False):
        super().__init__(mapping=mapping, default_extra=default_extra,
                         msec=msec)
        self.app_name = app_name

    def format(self, record):
        return '{}: @cee: '.format(self.app_name) + super().format(record)


class ColorFormatter(logging.Formatter):

    def __init__(self, isatty, msg_sep='', fmt=None, date_fmt=None,
                 styles=None):
        super().__init__(datefmt=date_fmt)
        self.isatty = isatty
        self.msg_sep = msg_sep
        self.fmt = fmt or DEFAULT_FMT
        self.styles = styles or DEFAULT_STYLES

        procs = []
        for key, style in self.fmt:
            procs.append((key, PROC_MAP[key](self.styles, style)))
        self._procs = procs
        self._codes = CODES if isatty else NO_CODES

        self._highlight = lambda s: s
        if self.isatty:
            try:
                self._highlight = self._setup_highlight()
            except ImportError:
                pass

    def _setup_highlight(self):
        from pygments import highlight
        from pygments.lexers.python import PythonTracebackLexer
        from pygments.formatters.terminal import TerminalFormatter

        return partial(highlight, lexer=PythonTracebackLexer(),
                       formatter=TerminalFormatter())

    def _get_extra(self, record):
        for key, value in record.__dict__.items():
            if key not in _SKIP_ATTRS:
                yield key, _json_value(value)

    def format(self, record):
        extra = sorted(self._get_extra(record), key=itemgetter(0))
        message = {
            'created': self.formatTime(record),
            'level_name': record.levelname,
            'name': record.name,
            'message': record.getMessage() + (self.msg_sep if extra else ''),
            'extra': extra,
        }
        s = ' '.join(proc(message[key], record.levelname, self._codes)
                     for key, proc in self._procs)
        if record.exc_info:
            exc = ''.join(traceback.format_exception(*record.exc_info))
            s += '\n' + self._highlight(exc).rstrip('\n')
        return s
