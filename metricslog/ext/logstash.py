from logstash.handler_tcp import TCPLogstashHandler
from logstash.handler_udp import UDPLogstashHandler


class TCPMetricsHandler(TCPLogstashHandler):

    def __init__(self, host, port, formatter):
        super().__init__(host, port)
        self.formatter = formatter

    def makePickle(self, record):
        return self.formatter.format(record).encode('utf-8') + b'\n'


class UDPMetricsHandler(UDPLogstashHandler):

    def __init__(self, host, port, formatter):
        super().__init__(host, port)
        self.formatter = formatter

    def makePickle(self, record):
        return self.formatter.format(record).encode('utf-8') + b'\n'
