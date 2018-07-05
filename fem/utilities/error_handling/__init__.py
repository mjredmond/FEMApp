"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range


import os

skip_error_handling = os.environ.get('SkipErrorHandling', '0')


class DummyError(Exception):
    """Dummy exception that will never be caught."""


class MyExceptions(object):
    ValueError = ValueError
    TypeError = TypeError
    IndexError = IndexError
    AttributeError = AttributeError
    KeyError = KeyError


if skip_error_handling == '1':
    MyExceptions.ValueError = DummyError
    MyExceptions.TypeError = DummyError
    MyExceptions.IndexError = DummyError
    MyExceptions.AttributeError = DummyError
    MyExceptions.KeyError = DummyError
