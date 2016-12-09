from logstash.handler_tcp import TCPLogstashHandler
from logstash.handler_udp import UDPLogstashHandler

from .formatter import MetricsFormatter


class TCPMetricsHandler(TCPLogstashHandler):

    def __init__(self, host, port, default_extra=None):
        super().__init__(host, port)
        self.formatter = MetricsFormatter(default_extra=default_extra)

    def makePickle(self, record):
        return self.formatter.format(record).encode('utf-8') + b'\n'


class UDPMetricsHandler(UDPLogstashHandler):

    def __init__(self, host, port, default_extra=None):
        super().__init__(host, port)
        self.formatter = MetricsFormatter(default_extra=default_extra)

    def makePickle(self, record):
        return self.formatter.format(record).encode('utf-8') + b'\n'
