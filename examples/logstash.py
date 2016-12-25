import os
import time
import socket
import logging

from metricslog.types import Record, Field, Integer
from metricslog.manager import Manager
from metricslog.ext.logstash import UDPMetricsHandler
from metricslog.ext.formatter import LogstashFormatter


class Metrics(Record):
    foo = Field('foo', Integer)


metrics_log = logging.getLogger('metrics')
metrics_log.setLevel(logging.INFO)
metrics_log.addHandler(UDPMetricsHandler(
    'logstash', 5959,
    LogstashFormatter(
        default_extra={
            'app': 'my-app-name',
            'host': socket.gethostname(),
            'pid': os.getpid(),
        },
    ),
))

metrics = Manager(Metrics(), interval_size=2, logger_name=metrics_log.name)

plain_log = logging.getLogger('logger')
plain_log.setLevel(logging.INFO)
plain_log.addHandler(UDPMetricsHandler(
    'logstash', 5959,
    LogstashFormatter(
        mapping={
            'message': 'message',
            'name': 'logger',
        },
        default_extra={
            'app': 'my-app-name',
            'host': socket.gethostname(),
            'pid': os.getpid(),
        },
        msec=True,
    ),
))

if __name__ == '__main__':
    plain_log.info('Something happened once', extra={'bar': 'baz1'})
    time.sleep(1)

    with metrics as m:
        m.foo.inc(5)
    time.sleep(3)  # metrics are flushed every 2 seconds
    metrics.ping()

    plain_log.info('Something happened twice', extra={'bar': 'baz2'})
    time.sleep(1)
