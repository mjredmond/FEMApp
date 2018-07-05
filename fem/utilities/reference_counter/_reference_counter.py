"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range


class ReferenceCounter(object):
    _refs = {}

    @classmethod
    def check(cls, obj):
        return cls._refs.get(id(obj), 0)

    def __init__(self, obj):

        self._id = id(obj)
        self._obj = obj

        try:
            self._refs[self._id] += 1
        except KeyError:
            self._refs[self._id] = 1

    def __del__(self):
        self._refs[self._id] -= 1

    def __getattr__(self, attr):
        return getattr(self._obj, attr)


if __name__ == '__main__':
    class A(object):
        def hello(self):
            print('hello')

    class Ref(ReferenceCounter):
        pass

    a = A()

    a_ = Ref(a)

    print(ReferenceCounter.check(a))

    a_.hello()
    a_ = None

    print(ReferenceCounter.check(a))