from logging.handlers import SysLogHandler, SYSLOG_UDP_PORT

from .formatter import MetricsFormatter


class MetricsSysLogHandler(SysLogHandler):

    def __init__(self, address=('localhost', SYSLOG_UDP_PORT),
                 application_name=None, default_extra=None,
                 **kwargs):
        super().__init__(address, **kwargs)
        self.ident = '{}: '.format(application_name or '')
        self.formatter = MetricsFormatter(default_extra=default_extra)

    def format(self, record):
        return '@cee: ' + super().format(record)
