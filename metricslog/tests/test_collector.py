from decimal import Decimal as Dec
from datetime import datetime

import pytest

from ..types import Integer, Float, Decimal, String, Timestamp, UNSET
from ..types import Map, Record, Field
from ..collector import collect, Nothing


@pytest.mark.parametrize('metric_cls, value', [
    (Integer, 5),
    (Float, 5.1),
    (Decimal, Dec('5.1')),
    (String, 'deaness'),
    (Timestamp, datetime.now()),
])
def test_collect_simple_set(metric_cls, value):
    metric = metric_cls()
    assert metric.dirty is False
    assert metric.flush is False
    # initially nothing to collect
    with pytest.raises(Nothing):
        collect(metric)

    metric.set(value)
    assert metric.dirty is True
    assert metric.flush is False

    assert collect(metric) == value
    # collect preserves set value
    assert metric.__value__ == value
    assert metric.dirty is False
    assert metric.flush is False

    # second attempts should fail
    with pytest.raises(Nothing):
        collect(metric)


@pytest.mark.parametrize('metric_cls, value', [
    (Integer, 6),
    (Float, 4.1),
    (Decimal, Dec('7.1')),
])
def test_collect_simple_acc(metric_cls, value):
    metric = metric_cls()
    assert metric.dirty is False
    assert metric.flush is False
    # initially nothing to collect
    with pytest.raises(Nothing):
        collect(metric)

    metric.inc(value)
    assert metric.__value__ == value
    assert metric.dirty is True
    assert metric.flush is True

    assert collect(metric) == value
    # collect should unset value (flush)
    assert metric.__value__ is UNSET
    assert metric.dirty is False
    assert metric.flush is False


def test_collect_map():
    metric_type = Map[str, Integer]
    metric = metric_type()
    # initially nothing to collect
    with pytest.raises(Nothing):
        collect(metric)

    metric['craws'].inc(1)
    assert collect(metric) == {'craws': 1}

    # second attempts should fail
    with pytest.raises(Nothing):
        collect(metric)

    metric['craws'].inc(5)
    metric['craws'].inc(6)
    assert collect(metric) == {'craws': 5 + 6}


def test_collect_record():
    class Needeth(Record):
        traven = Field('farer', Integer)

    metric = Needeth()
    # initially nothing to collect
    with pytest.raises(Nothing):
        collect(metric)

    metric.traven.inc(1)
    assert collect(metric) == {'farer': 1}

    # second attempts should fail
    with pytest.raises(Nothing):
        collect(metric)

    metric.traven.inc(7)
    metric.traven.inc(8)
    assert collect(metric) == {'farer': 7 + 8}
