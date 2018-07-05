"""
mrsignal.mrsignal

MrSignal mimics the behavior of a Qt signal.  It can be used as a drop-in replacement for a Qt signal with the
exception that it does not respect argument types for signals.

author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems

import weakref
import inspect

from collections import OrderedDict
import sys
import traceback


ref = weakref.ref


class AbstractSlot(object):
    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def key(self):
        raise NotImplementedError


class RegularSlot(AbstractSlot):
    def __init__(self, slot):
        super(AbstractSlot, self).__init__()
        self._func = weakref.ref(slot)

    def execute(self, *args, **kwargs):
        func = self._func()

        if func is None:
            return

        #try:
        return func(*args, **kwargs)
        #except Exception as e:
        #    msg = "%s\n%s(%s, %s)\n" % ("Error in MrSignal!", func.__name__, str(args), str(kwargs))
        #    raise Exception, msg + "%s" % str(e), sys.exc_info()[2]

    def key(self):
        return str(self._func())


class MethodSlot(AbstractSlot):
    def __init__(self, slot):
        super(AbstractSlot, self).__init__()
        self._self = weakref.ref(slot.__self__)
        self._func = weakref.ref(slot.__func__)

    def execute(self, *args, **kwargs):
        obj = self._self()
        if obj is None:
            return
        func = self._func()
        if func is None:
            return
        #try:
        return func(obj, *args, **kwargs)
        #except Exception as e:
        #    msg = "%s\n%s.%s(%s, %s)\n" % (
        #        "Error in MrSignal!", obj.__class__.__name__, func.__name__, str(args), str(kwargs))
        #    raise Exception, msg + "%s" % e, sys.exc_info()[2]

    def key(self):
        return str((self._self(), self._func()))


class MrSignal(object):
    def __init__(self):
        # self._slots = OrderedDict()
        self._slots = []
        self._blocked = False
        self._interception = None

        self.emit = self._emit_to_slots
        self.responders = []
        self.results = []

    def connect(self, slot):
        if inspect.ismethod(slot):
            new_slot = MethodSlot(slot)
        else:
            new_slot = RegularSlot(slot)

        # self._slots[new_slot.key()] = new_slot
        self._slots.append((new_slot.key(), new_slot))

    def disconnect(self, slot):
        if inspect.ismethod(slot):
            delete_slot = MethodSlot(slot)
        else:
            delete_slot = RegularSlot(slot)

        # try:
        #     del self._slots[delete_slot.key()]
        # except Exception:
        #     pass

        slot_key = delete_slot.key()

        for i in range(len(self._slots)):
            if slot_key == self._slots[i][0]:
                del self._slots[i]

    def disconnect_all(self):
        # self._slots.clear()
        del self._slots[:]

    def intercept(self, slot):
        if inspect.ismethod(slot):
            new_slot = MethodSlot(slot)
        else:
            new_slot = RegularSlot(slot)

        self._interception = new_slot
        self.emit = self._emit_to_interception

    def remove_intercept(self):
        self._interception = None
        self.emit = self._emit_to_slots

    def block(self):
        self._blocked = True

    def unblock(self):
        self._blocked = False

    def _emit_to_slots(self, *args, **kwargs):
        del self.responders[:]
        del self.results[:]

        if self._blocked:
            return

        # for key, slot in iteritems(self._slots):
        #     self.results.append(slot.execute(*args, **kwargs))
        #     self.responders.append(key)

        for _slot in self._slots:
            key, slot = _slot
            self.results.append(slot.execute(*args, **kwargs))
            self.responders.append(key)

    def _emit_to_interception(self, *args, **kwargs):
        del self.responders[:]
        del self.results[:]

        if self._blocked:
            return

        self.results.append(self._interception.execute(*args, **kwargs))
        self.responders.append(self._interception.key())


class DummyObject(object):
    def __init__(self):
        self.signal1 = MrSignal()
        self.signal2 = MrSignal()

    def dummy_slot(self, data):
        print("dummy slot %s" % data)


def dummy_func(data):
    print("function %s" % data)


if __name__ == "__main__":
    a = DummyObject()
    b = DummyObject()

    a.signal1.connect(b.dummy_slot)
    a.signal1.connect(dummy_func)

    a.signal1.emit("1")
