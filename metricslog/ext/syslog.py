from logging.handlers import SysLogHandler

from .formatter import MetricsFormatter


class MetricsSysLogHandler(SysLogHandler):

    def __init__(self, *args, default_extra=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = MetricsFormatter(default_extra=default_extra)

    def format(self, record):
        return '@cee: ' + super().format(record)
