import abc
import decimal

from collections import defaultdict

from .compat import with_metaclass


UNSET = object()


class Type(with_metaclass(abc.ABCMeta, object)):

    @abc.abstractmethod
    def accept(self, visitor):
        pass

    @abc.abstractmethod
    def clear(self):
        pass


class SetMixin:
    dirty = False
    flush = False

    __value__ = UNSET

    def set(self, value):
        self.__value__ = value
        self.dirty = True

    def clear(self):
        if self.__value__ is not UNSET:
            del self.__value__
        if self.dirty:
            del self.dirty
        if self.flush:
            del self.flush

    def was_detected(self):
        if self.dirty:
            del self.dirty
        if self.flush:
            self.clear()


class AccMixin(SetMixin):

    @abc.abstractproperty
    def __default__(self):
        pass

    def inc(self, value):
        if self.__value__ is UNSET:
            self.__value__ = self.__default__
        self.__value__ += value
        self.dirty = True
        self.flush = True


class Integer(AccMixin, Type):
    __default__ = 0

    def accept(self, visitor):
        return visitor.visit_integer(self)


class Float(AccMixin, Type):
    __default__ = 0.0

    def accept(self, visitor):
        return visitor.visit_float(self)


class Decimal(AccMixin, Type):
    __default__ = decimal.Decimal()

    def accept(self, visitor):
        return visitor.visit_decimal(self)


class String(SetMixin, Type):

    def accept(self, visitor):
        return visitor.visit_string(self)


class Timestamp(SetMixin, Type):

    def accept(self, visitor):
        return visitor.visit_timestamp(self)


class MapMeta(abc.ABCMeta):

    def __getitem__(cls, params):
        key_type, value_type = params
        if not isinstance(key_type, type):
            raise TypeError('Key type is not a type: {!r}'
                            .format(key_type))
        if not isinstance(value_type, type):
            raise TypeError('Value type is not a type: {!r}'
                            .format(value_type))
        type_ = cls.__class__(cls.__name__, cls.__bases__, dict(cls.__dict__))
        type_.__key_type__ = key_type
        type_.__value_type__ = value_type
        return type_


class Map(with_metaclass(MapMeta, Type)):
    __key_type__ = None
    __value_type__ = None

    def __init__(self):
        if not self.__key_type__ or not self.__value_type__:
            raise TypeError('Can not instantiate Map without params')
        self.__items__ = defaultdict(self.__value_type__)

    def __getitem__(self, key):
        if not isinstance(key, self.__key_type__):
            raise TypeError('Invalid key type: {!r}; expected: {!r}'
                            .format(type(key), self.__key_type__))
        return self.__items__[key]

    def accept(self, visitor):
        return visitor.visit_map(self)

    def clear(self):
        self.__items__.clear()


class Field:

    def __init__(self, name, type_):
        self.name = name
        self.type = type_


class RecordMeta(abc.ABCMeta):

    def __new__(mcs, name, bases, params):
        cls = super(RecordMeta, mcs).__new__(mcs, name, bases, params)
        field_types = {}
        for name, attr in params.items():
            if isinstance(attr, Field):
                field_types[name] = attr
        cls.__field_types__ = field_types
        return cls


class Record(with_metaclass(RecordMeta, Type)):
    __field_types__ = None

    def __init__(self):
        self.__fields__ = {
            field.name: field.type()
            for field in self.__field_types__.values()
        }
        self.__dict__.update({
            name: self.__fields__[field.name]
            for name, field in self.__field_types__.items()
        })

    def accept(self, visitor):
        return visitor.visit_record(self)

    def clear(self):
        for field_type in self.__fields__.values():
            field_type.clear()
