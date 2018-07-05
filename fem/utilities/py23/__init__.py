"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems, itervalues, iterkeys

import sys

py_version = sys.version_info[0]


if py_version == 2:
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    unicode = unicode
    bytes = str
    # noinspection PyUnresolvedReferences, PyUnboundLocalVariable
    range = xrange

else:
    unicode = str
    bytes = bytes
    xrange = range
