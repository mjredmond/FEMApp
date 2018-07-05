"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems

from qtpy import QtWidgets, QtCore, QtGui

from ._basic_table import BasicTable
from fem.utilities.command_dispatcher import CommandDispatcher, ChildCommand, dispatcher_version
from fem.utilities import MrSignal


assert dispatcher_version == '3'


class _ChildCommand(ChildCommand):
    def __init__(self, command, tab_widget):
        super(_ChildCommand, self).__init__(command)

        self.tab_widget = tab_widget
        """:type: BasicTabWidget"""

        self.index = self.tab_widget.currentIndex()

    def redo(self):
        if self.command.skip_first:
            self.command.skip_first = False
            return

        self.tab_widget.setCurrentIndex(self.index)
        self.command.redo()

    def undo(self):
        self.tab_widget.setCurrentIndex(self.index)
        self.command.undo()


class _CommandDispatcher(CommandDispatcher):
    def __init__(self, dispatcher_id, tab_widget):
        super(_CommandDispatcher, self).__init__(dispatcher_id)

        self.tab_widget = tab_widget
        """:type: BasicTabWidget"""

    def _wrap_command(self, command):
        command = _ChildCommand(self._get_command(command), self.tab_widget)

        try:
            return self._parent_dispatcher._wrap_command(command)
        except AttributeError:
            return command


class BasicTabWidget(QtWidgets.QTabWidget):
    def __init__(self, tab_name, parent=None):
        super(BasicTabWidget, self).__init__(parent)

        self.tab_name = tab_name

        self.dispatcher = _CommandDispatcher(tab_name, self)

        self.tables = {}

        self.data_changed = MrSignal()

    def add_table(self, table, name, prefix):
        """

        :param table:
        :type table: BasicTable
        :param name:
        :type name: str
        :param prefix:
        :type prefix: str
        :return:
        :rtype:
        """

        self.dispatcher.add_child(table.dispatcher)

        self.addTab(table, name)

        self.tables[name] = table

        table.table_1.data_changed.connect(self._data_changed)
        table.table_2.data_changed.connect(self._data_changed)

    def _data_changed(self, *args):
        self.data_changed.emit()

    def keyPressEvent(self, event):
        super(BasicTabWidget, self).keyPressEvent(event)

        if event.isAccepted():
            return

        if event.matches(QtGui.QKeySequence.Undo):
            event.accept()
            self.dispatcher.dispatch('Undo')

        elif event.matches(QtGui.QKeySequence.Redo):
            event.accept()
            self.dispatcher.dispatch('Redo')

    def serialize(self):
        data = []
        for key, table in iteritems(self.tables):
            data.append([key, table.serialize()])

        return data

    def load(self, data):
        for data_ in data:
            key, _data = data_
            self.tables[key].load(_data)

    def clear(self):
        for key, table in iteritems(self.tables):
            table.clear()

    def update_all(self):
        for key, table in iteritems(self.tables):
            table.update_all()
