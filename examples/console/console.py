import time
import os.path
import logging.config

import yaml

from metricslog.types import Record, Field, Integer
from metricslog.manager import Manager


log = logging.getLogger('app')


class Metrics(Record):
    counter = Field('counter', Integer)


metrics = Manager(Metrics(), interval_size=2, logger_name='metrics')


def fail_func():
    1/0


def main():
    log.info('First event', extra={'user': 1})
    time.sleep(1)

    with metrics as m:
        m.counter.inc(5)
    time.sleep(3)  # metrics are flushed every 2 seconds
    metrics.ping()

    log.info('Second event', extra={'user': 2})
    time.sleep(1)
    try:
        fail_func()
    except Exception:
        log.exception('Sorry, can\'t divide by zero')


if __name__ == '__main__':
    console_yaml = os.path.join(os.path.dirname(__file__), 'logging.yaml')

    with open(console_yaml) as f:
        logging.config.dictConfig(yaml.load(f))

    main()
