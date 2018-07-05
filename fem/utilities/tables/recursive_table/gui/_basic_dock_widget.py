"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtCore, QtGui

from ._basic_tab_widget import BasicTabWidget

from fem.utilities import MrSignal
from fem.utilities.command_dispatcher import CommandDispatcherWrapper, ChildCommand, dispatcher_version


assert dispatcher_version == '4'


class _ChildCommand(ChildCommand):
    def __init__(self, command, dock_widget):
        super(_ChildCommand, self).__init__(command)

        self.dock_widget = dock_widget
        """:type: BasicDockWidget"""

    def redo(self):
        if self.command.skip_first:
            self.command.skip_first = False
            return

        self.dock_widget.request_focus()
        self.command.redo()

    def undo(self):
        self.dock_widget.request_focus()
        self.command.undo()


# noinspection PyProtectedMember
class _CommandDispatcher(CommandDispatcherWrapper):
    def __init__(self, dispatcher_id, dock_widget):
        super(_CommandDispatcher, self).__init__(dispatcher_id)

        self.dock_widget = dock_widget
        """:type: BasicDockWidget"""

    def _wrap_command(self, command):
        command = _ChildCommand(command, self.dock_widget)

        try:
            return self._parent_dispatcher._wrap_command(command)
        except AttributeError:
            return command


class BasicDockWidget(QtWidgets.QDockWidget):
    def __init__(self, dock_name='BasicDockWidget'):
        super(BasicDockWidget, self).__init__()

        self.dock_name = dock_name

        self.setWindowTitle(dock_name)

        self.dispatcher = _CommandDispatcher(dock_name, self)

        self.widget = None

        self.show_dock = MrSignal()

        self.data_changed = MrSignal()
        """:type: MrSignal"""

    def set_widget(self, tab_widget):
        try:
            self.widget.data_changed.disconnect_all()
        except AttributeError:
            pass

        self.widget = tab_widget
        self.setWidget(self.widget)

        self.dispatcher.add_child(self.widget.dispatcher)

        try:
            self.widget.data_changed.connect(self._data_changed)
        except AttributeError:
            pass

    def _data_changed(self, *args):
        self.data_changed.emit()

    def request_focus(self):
        self.show()
        self.raise_()

    def keyPressEvent(self, event):
        super(BasicDockWidget, self).keyPressEvent(event)

        if event.isAccepted():
            return

        if event.matches(QtGui.QKeySequence.Undo):
            event.accept()
            self.dispatcher.dispatch('Undo')

        elif event.matches(QtGui.QKeySequence.Redo):
            event.accept()
            self.dispatcher.dispatch('Redo')

    def serialize(self):
        return self.widget.serialize()

    def load(self, data):
        self.widget.load(data)

    def clear(self):
        self.widget.clear()

    def update_all(self):
        self.widget.update_all()

    def clear_data(self):
        try:
            self.widget.clear_data()
        except AttributeError:
            pass
