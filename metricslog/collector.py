class Nothing(Exception):
    pass


class Collector:

    def visit(self, obj):
        return obj.accept(self)

    def _visit_scalar(self, obj):
        if obj.dirty:
            value = obj.__value__
            obj.was_detected()
            return value
        else:
            raise Nothing('Metric not changed')

    visit_integer = visit_float = visit_decimal = visit_string = \
        visit_timestamp = _visit_scalar

    def visit_map(self, obj):
        d = {}
        for key, value in obj.__items__.items():
            try:
                d[key] = self.visit(value)
            except Nothing:
                pass
        if not d:
            raise Nothing('Map not changed')
        return d

    def visit_record(self, obj):
        d = {}
        for field_name, field_type in obj.__fields__.items():
            try:
                d[field_name] = self.visit(field_type)
            except Nothing:
                pass
        if not d:
            raise Nothing('Record not changed')
        return d


def collect(metric):
    collector = Collector()
    return collector.visit(metric)
