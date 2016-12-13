import time
import logging

from logging.handlers import SysLogHandler

from metricslog.types import Record, Field, Integer
from metricslog.manager import Manager
from metricslog.ext.syslog import MetricsSysLogHandler

log = logging.getLogger('metrics1')
log.setLevel(logging.INFO)
log.addHandler(MetricsSysLogHandler(address='/dev/log',
                                    facility='local3'))
log.info('foo', extra={'foo': 'bar'})

log1 = logging.getLogger('metrics2')
log1.setLevel(logging.INFO)
log1.addHandler(MetricsSysLogHandler(address='/dev/log',
                                     application_name='messenger.uaprom',
                                     facility='local3'))
log1.info('foo', extra={'foo': 'bar'})

log2 = logging.getLogger('product.main')
log2.setLevel(logging.INFO)
log2.addHandler(SysLogHandler('/dev/log', facility='local3'))
log2.info(': @cee: {"msg": "Something happened", "logger": "product.main"}')
log2.info('product.uaprom: @cee: {"msg": "Something happened", "logger": "product.main"}')


# class Metrics(Record):
#     foo = Field('foo', Integer)
#
# metrics = Manager(Metrics())
#
# with metrics as m:
#     m.foo.inc(5)
#
# # metricslog flushes metrics every 10 seconds by default
# time.sleep(10)
#
# metrics.ping()
