"""
command_dispatacher.action

Defines action

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import


class ActionData(object):
    def __init__(self, *args):
        pass

    def __str__(self):
        raise NotImplementedError


class Action(object):
    action_name = None
    ActionDataCls = None
    log_action = True

    def __init__(self, main_data, action_data):
        self.main_data = main_data

        if isinstance(action_data, self.ActionDataCls):
            self.action_data = action_data
        elif isinstance(action_data, tuple):
            self.action_data = self.ActionDataCls(*action_data)
        else:
            raise TypeError('%s: action_data must be either a tuple or %s! (%s)' %
                            (self.action_name, self.ActionDataCls.__name__, type(action_data)))

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

    def _redo(self):
        raise NotImplementedError

    def _undo(self):
        raise NotImplementedError

    def _validate(self):
        raise NotImplementedError

    def _before_redo(self):
        raise NotImplementedError

    def _after_redo(self):
        raise NotImplementedError

    def _before_undo(self):
        raise NotImplementedError

    def _after_undo(self):
        raise NotImplementedError

    def __str__(self):
        return '%s%s' % (self.action_name, str(self.action_data))
