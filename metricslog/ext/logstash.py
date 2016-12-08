from logstash.formatter import LogstashFormatterBase
from logstash.handler_tcp import TCPLogstashHandler
from logstash.handler_udp import UDPLogstashHandler


class MetricsFormatter(LogstashFormatterBase):

    def __init__(self, default_extra=None):
        super().__init__()
        self.default_extra = default_extra or {}

    def format(self, record):
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'host': self.host,
            'type': 'metricslog',
        }

        # add default extra fields
        message.update(self.default_extra)

        # add extra fields
        extra = self.get_extra_fields(record)
        extra.pop('stack_info', None)
        message.update(extra)

        return self.serialize(message)


class TCPMetricsHandler(TCPLogstashHandler):

    def __init__(self, host, port, default_extra=None):
        super().__init__(host, port)
        self.formatter = MetricsFormatter(default_extra=default_extra)


class UDPMetricsHandler(UDPLogstashHandler):

    def __init__(self, host, port, default_extra=None):
        super().__init__(host, port)
        self.formatter = MetricsFormatter(default_extra=default_extra)
