"""
command_dispatacher.command

Defines command

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtCore, QtGui, QtWidgets

from .action import Action


class Command(QtWidgets.QUndoCommand):
    command_name = None
    push_to_stack = True
    set_clean = False

    def __init__(self, main_window, action, *args):
        super(Command, self).__init__(*args)

        assert isinstance(main_window, QtWidgets.QWidget)
        self.main_window = main_window
        """:type: QtGui.QWidget"""

        assert isinstance(action, Action)
        self.action = action
        """:type: Action"""

        self.skip_first = True

        self.command_result = False

    def _get_main_window(self):
        return self.main_window

    def redo(self):
        if self.skip_first:
            self.skip_first = False
            self.command_result = True
            return

        self._before_redo()

        redo_result = self.action.redo()

        if redo_result:
            self._after_redo()

        self.command_result = redo_result

    def undo(self):
        self._before_undo()
        self.action.undo()
        self._after_undo()

    def _before_redo(self):
        raise NotImplementedError

    def _after_redo(self):
        raise NotImplementedError

    def _before_undo(self):
        raise NotImplementedError

    def _after_undo(self):
        raise NotImplementedError
