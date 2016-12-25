import time
import logging

from logging.handlers import SysLogHandler

from metricslog.types import Record, Field, Integer
from metricslog.manager import Manager
from metricslog.ext.formatter import CEELogstashFormatter


class Metrics(Record):
    foo = Field('foo', Integer)


metrics_log_handler = SysLogHandler('/dev/log', facility='local3')
metrics_log_handler.formatter = CEELogstashFormatter('my-app-name')

metrics_log = logging.getLogger('metrics')
metrics_log.setLevel(logging.INFO)
metrics_log.addHandler(metrics_log_handler)

metrics = Manager(Metrics(), interval_size=2, logger_name=metrics_log.name)

plain_log_handler = SysLogHandler('/dev/log', facility='local3')
plain_log_handler.formatter = CEELogstashFormatter(
    'my-app-name',
    mapping={'message': 'message', 'name': 'logger'},
    msec=True,
)

plain_log = logging.getLogger('path.to.module')
plain_log.setLevel(logging.INFO)
plain_log.addHandler(plain_log_handler)

if __name__ == '__main__':
    plain_log.info('Something happened once', extra={'bar': 'baz1'})
    time.sleep(1)

    with metrics as m:
        m.foo.inc(5)
    time.sleep(3)  # metrics are flushed every 2 seconds
    metrics.ping()

    plain_log.info('Something happened twice', extra={'bar': 'baz2'})
    time.sleep(1)
