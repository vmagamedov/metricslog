from decimal import Decimal as Dec
from datetime import datetime

import pytest

from ..types import Integer, Float, Decimal, String, Timestamp
from ..types import Map, Record, Field


@pytest.mark.parametrize('metric_cls, value', [
    (Integer, 5),
    (Float, 5.1),
    (Decimal, Dec('5.1')),
    (String, 'deaness'),
    (Timestamp, datetime.now()),
])
def test_set(metric_cls, value):
    metric = metric_cls()
    assert metric.dirty is False
    metric.set(value)
    assert metric.dirty is True
    assert metric.__value__ == value
    metric.clear()
    assert metric.dirty is False


@pytest.mark.parametrize('metric_cls, first, second, sum_', [
    (Integer, 5, 3, 8),
    (Float, 5.1, 3.2, pytest.approx(8.3)),
    (Decimal, Dec('5.1'), Dec('3.2'), Dec('8.3')),
])
def test_acc(metric_cls, first, second, sum_):
    metric = metric_cls()
    assert metric.dirty is False
    assert metric.flush is False
    metric.inc(first)
    assert metric.dirty is True
    assert metric.flush is True
    assert metric.__value__ == first
    metric.inc(second)
    assert metric.__value__ == sum_
    metric.clear()
    assert metric.dirty is False
    assert metric.flush is False


def test_map():
    metric_type = Map[str, Integer]
    metric = metric_type()
    assert not metric.__items__
    assert metric['scheldt'].dirty is False
    assert metric.__items__

    metric['scheldt'].inc(1)
    assert metric['scheldt'].dirty is True

    metric.clear()
    assert not metric.__items__


def test_record():
    class Sickly(Record):
        chevaux = Field('charqui', Integer)

    metric = Sickly()
    assert metric.__fields__ == {'chevaux': metric.chevaux}
    assert metric.chevaux.dirty is False
    metric.chevaux.inc(1)
    assert metric.chevaux.dirty is True
    metric.clear()
    assert metric.chevaux.dirty is False
