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
    main_window = None
    MainWindow = None

    push_to_stack = True
    set_clean = False

    def __init__(self, action, main_window=None, *args):
        super(Command, self).__init__(*args)

        if main_window is not None:
            self.main_window = main_window
            """:type: QtGui.QWidget"""

        else:
            try:
                assert self.MainWindow or self.main_window
            except AssertionError:
                print(self.MainWindow, self.main_window)

            self.main_window = self._get_main_window()
            """:type: QtGui.QWidget"""

        assert isinstance(action, Action)
        self.action = action
        """:type: Action"""

        self.skip_first = True

        self.command_result = False

    def finalize(self):
        self.command_name = None
        self.main_window = None
        self.MainWindow = None
        self.action.finalize()
        self.action = None

    def _get_main_window(self):
        if self.main_window is None:
            self.main_window = self.MainWindow.instance()

        return self.main_window

    def _before_redo(self):
        raise NotImplementedError

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

    def _after_redo(self):
        raise NotImplementedError

    def _before_undo(self):
        raise NotImplementedError

    def undo(self):
        self._before_undo()
        self.action.undo()
        self._after_undo()

    def _after_undo(self):
        raise NotImplementedError

    def __str__(self):
        return str(self.action)


class ChildCommand(QtWidgets.QUndoCommand):
    def __init__(self, command):
        super(ChildCommand, self).__init__(command)

        self.command = command
        """:type: Command"""

        self._command_name = None

    def redo(self):
        self.command.redo()

    def undo(self):
        self.command.undo()

    def finalize(self):
        self.command.finalize()
        self.command = None

    @property
    def command_name(self):
        if self._command_name is None:
            return self.command.command_name

        return self._command_name

    @command_name.setter
    def command_name(self, value):
        self._command_name = value

    @property
    def main_window(self):
        return self.command.main_window

    @property
    def push_to_stack(self):
        return self.command.push_to_stack

    @property
    def set_clean(self):
        return self.command.set_clean

    @property
    def skip_first(self):
        return self.command.skip_first

    @skip_first.setter
    def skip_first(self, value):
        self.command.skip_first = value

    @property
    def command_result(self):
        return self.command.command_result

    @command_result.setter
    def command_result(self, value):
        self.command.command_result = value

    @property
    def action(self):
        return self.command.action

    def __str__(self):
        return str(self.command)
