from __future__ import unicode_literals

import os
import time
import json
import socket
import logging

import pytest

from ..ext.formatter import LogstashFormatter, CEELogstashFormatter


NOW = time.time()


class HandlerStub(logging.Handler):

    def __init__(self, timestamp, level=logging.NOTSET):
        super(HandlerStub, self).__init__(level=level)
        self._timestamp = timestamp
        self._buffer = []

    def emit(self, record):
        record.created = self._timestamp
        record.msecs = (self._timestamp - int(NOW)) * 1000
        self._buffer.append(self.format(record))

    def logs(self):
        return self._buffer[:]


@pytest.mark.parametrize('timestamp, iso_timestamp', [
    (1445850000, '2015-10-26T09:00:00.000Z'),
    (1445850000.1114111, '2015-10-26T09:00:00.111Z'),
    (1445850000.1116111, '2015-10-26T09:00:00.112Z'),
])
def test_logstash_formatter(timestamp, iso_timestamp):
    handler = HandlerStub(timestamp, level=logging.DEBUG)
    handler.setFormatter(LogstashFormatter())

    log = logging.getLogger('does-not-matter')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('does-not-matter', extra={'pampas': 'semi'})

    msg, = handler.logs()
    doc = json.loads(msg)

    assert doc == {'@timestamp': iso_timestamp,
                   '@version': '1',
                   'pampas': 'semi'}


def test_logstash_formatter_mapping():
    handler = HandlerStub(1445850000, level=logging.DEBUG)
    handler.setFormatter(LogstashFormatter(mapping={
        'name': 'pleurae',
        'message': 'lansat',
    }))

    log = logging.getLogger('bashan')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('basset-devours-manus', extra={'flushed': 'impen'})

    msg, = handler.logs()
    doc = json.loads(msg)

    assert doc == {'@timestamp': '2015-10-26T09:00:00.000Z',
                   '@version': '1',
                   'flushed': 'impen',
                   'pleurae': 'bashan',
                   'lansat': 'basset-devours-manus'}


def test_logstash_formatter_defaults():
    handler = HandlerStub(1445850000, level=logging.DEBUG)
    handler.setFormatter(LogstashFormatter(defaults={
        'itchy': 'saws',
        'craft': '<host>',
        'colure': '<pid>',
    }))

    log = logging.getLogger('does-not-matter')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('does-not-matter', extra={'taxicab': 'wakashu'})

    msg, = handler.logs()
    doc = json.loads(msg)

    assert doc == {'@timestamp': '2015-10-26T09:00:00.000Z',
                   '@version': '1',
                   'taxicab': 'wakashu',
                   'itchy': 'saws',
                   'craft': socket.gethostname(),
                   'colure': os.getpid()}


@pytest.mark.parametrize('timestamp, iso_timestamp', [
    (1445850000, '2015-10-26T09:00:00.000Z'),
    (1445850000.1114111, '2015-10-26T09:00:00.111Z'),
    (1445850000.1116111, '2015-10-26T09:00:00.112Z'),
])
def test_cee_formatter(timestamp, iso_timestamp):
    app_name = 'fuss'
    prefix = '{}: @cee: '.format(app_name)

    handler = HandlerStub(timestamp, level=logging.DEBUG)
    handler.setFormatter(CEELogstashFormatter(app_name))

    log = logging.getLogger('does-not-matter')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('does-not-matter', extra={'guff': 'noelle'})

    msg, = handler.logs()
    assert msg.startswith(prefix)
    doc = json.loads(msg[len(prefix):])

    assert doc == {'@timestamp': iso_timestamp,
                   '@version': '1',
                   'guff': 'noelle'}
