import sys


PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
    string_types = str,

else:
    text_type = unicode  # noqa
    string_types = basestring,  # noqa


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""

    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
