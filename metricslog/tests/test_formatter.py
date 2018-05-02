# coding: utf-8
from __future__ import unicode_literals

import os
import json
import socket
import logging

from decimal import Decimal
from datetime import datetime

import pytest

from ..ext._colors import CODES
from ..ext.formatter import LogstashFormatter, CEELogstashFormatter
from ..ext.formatter import ColorFormatter


class HandlerStub(logging.Handler):

    def __init__(self, timestamp, level=logging.NOTSET):
        super(HandlerStub, self).__init__(level=level)
        self._timestamp = timestamp
        self._buffer = []

    def emit(self, record):
        record.created = self._timestamp
        record.msecs = (self._timestamp - int(self._timestamp)) * 1000
        self._buffer.append(self.format(record))

    def logs(self):
        return self._buffer[:]


def get_logger(name, timestamp, formatter):
    handler = HandlerStub(timestamp, level=logging.DEBUG)
    handler.setFormatter(formatter)

    log = logging.getLogger(name)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    return log, handler


@pytest.mark.parametrize('timestamp, iso_timestamp', [
    (1445850000, '2015-10-26T09:00:00.000Z'),
    (1445850000.1114111, '2015-10-26T09:00:00.111Z'),
    (1445850000.1116111, '2015-10-26T09:00:00.112Z'),
])
def test_logstash_formatter(timestamp, iso_timestamp):
    log, handler = get_logger('does-not-matter', timestamp,
                              LogstashFormatter())

    log.info('does-not-matter', extra={'pampas': 'semi'})

    msg, = handler.logs()
    doc = json.loads(msg)

    assert doc == {'@timestamp': iso_timestamp,
                   '@version': '1',
                   'pampas': 'semi'}


def test_logstash_formatter_mapping():
    log, handler = get_logger('bashan', 1445850000, LogstashFormatter(mapping={
        'name': 'pleurae',
        'message': 'lansat',
    }))

    log.info('basset-devours-manus', extra={'flushed': 'impen'})

    msg, = handler.logs()
    doc = json.loads(msg)

    assert doc == {'@timestamp': '2015-10-26T09:00:00.000Z',
                   '@version': '1',
                   'flushed': 'impen',
                   'pleurae': 'bashan',
                   'lansat': 'basset-devours-manus'}


def test_logstash_formatter_defaults():
    log, handler = get_logger('any', 1445850000, LogstashFormatter(defaults={
        'itchy': 'saws',
        'craft': '<host>',
        'colure': '<pid>',
    }))

    log.info('does-not-matter', extra={'taxicab': 'wakashu'})

    msg, = handler.logs()
    doc = json.loads(msg)

    assert doc == {'@timestamp': '2015-10-26T09:00:00.000Z',
                   '@version': '1',
                   'taxicab': 'wakashu',
                   'itchy': 'saws',
                   'craft': socket.gethostname(),
                   'colure': os.getpid()}


def test_logstash_formatter_defaults_py2():
    log, handler = get_logger('any', 1445850000, LogstashFormatter(defaults={
        'oner': str('<host>'),
        'gac': str('<pid>'),
    }))

    log.info('does-not-matter')

    msg, = handler.logs()
    doc = json.loads(msg)

    assert doc == {'@timestamp': '2015-10-26T09:00:00.000Z',
                   '@version': '1',
                   'oner': socket.gethostname(),
                   'gac': os.getpid()}


@pytest.mark.parametrize('timestamp, iso_timestamp', [
    (1445850000, '2015-10-26T09:00:00.000Z'),
    (1445850000.1114111, '2015-10-26T09:00:00.111Z'),
    (1445850000.1116111, '2015-10-26T09:00:00.112Z'),
])
def test_cee_formatter(timestamp, iso_timestamp):
    app_name = 'fuss'
    prefix = '{}: @cee: '.format(app_name)

    log, handler = get_logger('any', timestamp, CEELogstashFormatter(app_name))

    log.info('does-not-matter', extra={'guff': 'noelle'})

    msg, = handler.logs()
    assert msg.startswith(prefix)
    doc = json.loads(msg[len(prefix):])

    assert doc == {'@timestamp': iso_timestamp,
                   '@version': '1',
                   'guff': 'noelle'}


def test_json_format():
    log, handler = get_logger('any', 1445850000, LogstashFormatter())

    unknown = object()

    extra = {
        'int_field': 111,
        'float_field': 111.111,
        'string_field': 'habitan',
        'date_field': datetime(2015, 10, 26, 9, 0, 1),
        'decimal_field': Decimal('111.111'),
        'unknown_field': unknown,
    }
    expected = {
        '@timestamp': '2015-10-26T09:00:00.000Z',
        '@version': '1',
        'int_field': 111,
        'float_field': pytest.approx(111.111),
        'string_field': 'habitan',
        'date_field': '2015-10-26T09:00:01.000Z',
        'decimal_field': '111.111',
        'unknown_field': str(unknown),
    }
    log.info('does-not-matter', extra=extra)
    msg, = handler.logs()
    doc = json.loads(msg)
    assert doc == expected


def test_color_formatter():
    log, handler = get_logger('any', 1445850000, ColorFormatter(False))

    unknown = object()

    extra = {
        'a': datetime(2015, 10, 26, 9, 0, 1),
        'b': 111,
        'c': 222.222,
        'd': Decimal('333.333'),
        'e': 'habitan',
        u'f': u'dure-юникод',
        'g': unknown,
    }

    log.info(u'does-not-matter-юникод', extra=extra)
    msg, = handler.logs()

    # `extra` items are sorted by ColorFormatter
    assert msg == (
        u'2015-10-26 11:00:00,000 INFO any does-not-matter-юникод '
        u'a=2015-10-26 09:00:01 '
        u'b=111 '
        u'c=222.222 '
        u'd=333.333 '
        u'e=habitan '
        u'f=dure-юникод '
        u'g={!r}'
        .format(unknown)
    )


def test_color_formatter_tty():
    log, handler = get_logger('any', 1445850000, ColorFormatter(True))

    unknown = object()

    extra = {
        'a': datetime(2015, 10, 26, 9, 0, 1),
        'b': 111,
        'c': 222.222,
        'd': Decimal('333.333'),
        'e': 'habitan',
        u'f': u'dure-юникод',
        'g': unknown,
    }

    log.info(u'does-not-matter-юникод', extra=extra)
    msg, = handler.logs()

    # `extra` items are sorted by ColorFormatter
    assert msg == (
        u'{white}2015-10-26 11:00:00,000{reset} '
        u'{green}INFO{reset} {white}any{reset} '
        u'{white}does-not-matter-юникод{reset} '
        u'{cyan}a={white}2015-10-26 09:00:01{reset} '
        u'{cyan}b={white}111{reset} '
        u'{cyan}c={white}222.222{reset} '
        u'{cyan}d={white}333.333{reset} '
        u'{cyan}e={white}habitan{reset} '
        u'{cyan}f={white}dure-юникод{reset} '
        u'{cyan}g={white}{0!r}{reset}'
        .format(unknown, **CODES)
    )


@pytest.mark.parametrize('extra_only', [{'foo'}, {'bar'}])
def test_extra_only(extra_only):
    log, handler = get_logger('foo.inner', 1445850000,
                              LogstashFormatter(extra_only=extra_only))
    log.info('message', extra={'a': 1})
    msg, = handler.logs()
    doc = json.loads(msg)
    if extra_only == {'foo'}:
        assert doc == {
            '@timestamp': '2015-10-26T09:00:00.000Z',
            '@version': '1',
            'a': 1,
        }
    else:  # bar
        assert doc == {
            '@timestamp': '2015-10-26T09:00:00.000Z',
            '@version': '1',
        }
