import time
import logging

from .collector import Nothing, collect


class Manager:

    def __init__(self, metrics, interval_size=10, logger_name='metrics'):
        self._metrics = metrics
        self._interval_size = interval_size

        self._interval = 0
        self._logger = logging.getLogger(logger_name)
        self._queue = []

    def __enter__(self):
        current_interval = int(time.time() // self._interval_size)
        if current_interval > self._interval:
            try:
                self._queue.append((self._interval, collect(self._metrics)))
            except Nothing:
                pass

        self._interval = current_interval
        return self._metrics

    def __exit__(self, exc_type, exc_val, exc_tb):
        while True:
            try:
                interval, data = self._queue.pop(0)
            except IndexError:
                break
            else:
                last_second = (interval + 1) * self._interval_size - 1
                fn, lno, func, sinfo = self._logger.findCaller()
                record = self._logger.makeRecord(
                    self._logger.name, logging.INFO, fn, lno, '-', [],
                    None, func=None, extra=data, sinfo=sinfo,
                )
                record.created = last_second
                record.msecs = 0
                self._logger.handle(record)

    def ping(self):
        """Optionally flush accumulated metrics"""
        with self:
            pass
