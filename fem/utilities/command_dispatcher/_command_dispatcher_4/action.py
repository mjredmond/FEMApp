"""
command_dispatacher.action

Defines action

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities.debug import debuginfo


class ActionData(object):
    def __init__(self, *args):
        pass

    def __str__(self):
        raise NotImplementedError

    def split(self):
        raise NotImplementedError


class DummyActionData(object):
    def __init__(self, *args):
        pass

    def __str__(self):
        return '()'

    def split(self):
        return None, None


class Action(object):
    action_name = None
    ActionDataCls = None
    main_data = None

    log_action = True

    def __init__(self, action_data):
        self.main_data = self.main_data

        try:
            assert isinstance(action_data, self.ActionDataCls)
        except AssertionError:
            debuginfo(action_data.__class__.__name__, action_data, self.ActionDataCls)
            raise

        self.action_data = action_data

        self.is_valid = True

    def redo(self):
        if not self.is_valid:
            return False

        self._before_redo()

        if not self._redo():
            return False

        self._after_redo()

        return True

    def undo(self):
        self._before_undo()
        self._undo()
        self._after_undo()

    def _before_redo(self):
        raise NotImplementedError

    def _redo(self):
        raise NotImplementedError

    def _after_redo(self):
        raise NotImplementedError

    def _before_undo(self):
        raise NotImplementedError

    def _undo(self):
        raise NotImplementedError

    def _after_undo(self):
        raise NotImplementedError

    def _validate(self):
        raise NotImplementedError

    def __str__(self):
        return '%s%s' % (self.action_name, str(self.action_data))

    def finalize(self):
        attrs = dir(self)

        for attr in attrs:
            try:
                setattr(self, attr, None)
            except Exception:
                pass
