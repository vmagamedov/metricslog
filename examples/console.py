import sys
import time
import logging

from metricslog.types import Record, Field, Integer
from metricslog.manager import Manager
from metricslog.ext.formatter import ColorFormatter


class Metrics(Record):
    foo = Field('foo', Integer)


console_handler = logging.StreamHandler()
console_handler.setFormatter(ColorFormatter(
    hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()
))

metrics_log = logging.getLogger('metrics')
metrics_log.setLevel(logging.INFO)
metrics_log.addHandler(console_handler)

plain_log = logging.getLogger('logger')
plain_log.setLevel(logging.INFO)
plain_log.addHandler(console_handler)

if __name__ == '__main__':
    metrics = Manager(Metrics(), interval_size=2, logger_name=metrics_log.name)

    plain_log.info('Something happened once', extra={'bar': 'baz1'})
    time.sleep(1)

    with metrics as m:
        m.foo.inc(5)
    time.sleep(3)  # metrics are flushed every 2 seconds
    metrics.ping()

    plain_log.info('Something happened twice', extra={'bar': 'baz2'})
    time.sleep(1)
