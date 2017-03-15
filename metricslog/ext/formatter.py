from __future__ import division

import os
import sys
import json
import socket
import logging
import datetime
import traceback

from operator import itemgetter
from functools import partial

from ..compat import text_type

from ._colors import DEFAULT_FMT, DEFAULT_STYLES, PROC_MAP, CODES, NO_CODES


_SKIP_ATTRS = {
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'message', 'msg', 'name', 'pathname', 'process',
    'processName', 'relativeCreated', 'thread', 'threadName', 'extra',
    'stack_info',
}

_SIMPLE_TYPES = (str, bool, dict, float, int, list)


def _json_value(value):
    return value if isinstance(value, _SIMPLE_TYPES) else str(value)


def _datetime_from_timestamp(timestamp):
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return (dt.strftime('%Y-%m-%dT%H:%M:%S')
            + '.{:03.0f}Z'.format(dt.microsecond / 1000))


def _maybe_special(value):
    if not isinstance(value, text_type):
        return value
    elif value == '<pid>':
        return os.getpid()
    elif value == '<host>':
        return socket.gethostname()
    else:
        return value


class LogstashFormatter(logging.Formatter):

    def __init__(self, mapping=None, defaults=None):
        super(LogstashFormatter, self).__init__()
        self.mapping = mapping or {}
        self.defaults = {k: _maybe_special(v)
                         for k, v in (defaults or {}).items()}

    def _get_extra(self, record):
        for key, value in record.__dict__.items():
            if value is not None and key not in _SKIP_ATTRS:
                yield key, _json_value(value)

    def _get_mapped(self, record):
        for from_, to in self.mapping.items():
            value = getattr(record, from_, None)
            if value is not None:
                yield to, _json_value(value)

    def format(self, record):
        record.message = record.getMessage()
        if record.exc_info and record.exc_text is None:
            record.exc_text = self.formatException(record.exc_info)

        # Note: - extra fields can not override mapped/defaults fields
        #       - mapped/default fields can not override @* fields

        message = dict(self._get_extra(record))
        message.update(self._get_mapped(record))
        message.update(self.defaults)
        message.update((
            ('@timestamp', _datetime_from_timestamp(record.created)),
            ('@version', '1'),
        ))
        return json.dumps(message)


class CEELogstashFormatter(LogstashFormatter):

    def __init__(self, app_name, mapping=None, defaults=None):
        super(CEELogstashFormatter, self).__init__(mapping=mapping,
                                                   defaults=defaults)
        self.app_name = app_name

    def format(self, record):
        doc = super(CEELogstashFormatter, self).format(record)
        return '{}: @cee: '.format(self.app_name) + doc


def _isatty():
    return hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()


class ColorFormatter(logging.Formatter):

    def __init__(self, isatty=None, msg_sep='', fmt=None, date_fmt=None,
                 styles=None):
        super(ColorFormatter, self).__init__(datefmt=date_fmt)
        self.isatty = _isatty() if isatty is None else isatty
        self.msg_sep = msg_sep
        self.fmt = fmt or DEFAULT_FMT
        self.styles = styles or DEFAULT_STYLES

        procs = []
        for key, style in self.fmt:
            procs.append((key, PROC_MAP[key](self.styles, style)))
        self._procs = procs
        self._codes = CODES if self.isatty else NO_CODES

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
