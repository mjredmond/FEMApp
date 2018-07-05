"""
command_dispatcher.undo_stack

Undo stack for command dispatcher

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtCore, QtGui, QtWidgets

from .command import Command


class UndoStack(QtWidgets.QUndoStack):
    def __init__(self, *args):
        super(UndoStack, self).__init__(*args)

    def push(self, command):
        assert isinstance(command, Command)
        super(UndoStack, self).push(command)
