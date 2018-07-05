"""
table_data_widget._table_data_widget

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from six.moves import range

from qtpy import QtWidgets, QtGui, QtCore

from .table_data_widget_ui import Ui_Form

from ._helpers import DataTable

from ..model import MainData
from ..configuration import Configuration
from ..actions import Actions, Commands

from fem.utilities.qtfile import getopenfilename
from fem.utilities import MrSignal


class TableDataWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        super(TableDataWidget, self).__init__(*args)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.tableView_list = DataTable.wrap_obj(self.ui.tableView_list)
        self.tableView_data = DataTable.wrap_obj(self.ui.tableView_data)

        self.tableView_list.set_editable_columns([0, 1])
        self.tableView_data.set_editable_columns([i for i in range(100)])

        self.ui.pushButton_add.clicked.connect(self._add)
        self.ui.pushButton_insert.clicked.connect(self._insert)
        self.ui.pushButton_delete.clicked.connect(self._delete)

        self.ui.pushButton_up.clicked.connect(self._up)
        self.ui.pushButton_down.clicked.connect(self._down)

        self.ui.pushButton_open.clicked.connect(self._open)

        self.main_data = MainData()
        """:type: fem.utilities.table_data_widget.model.MainData"""

        self.config = Configuration()

        self.tableView_list.setup_data(self.main_data.headers_1, self.main_data.interface1)
        self.tableView_data.setup_data(self.main_data.headers_2, self.main_data.interface2)

        self.tableView_list.selection_changed.connect(self._selection_changed)

        self.tableView_list.set_data_signal.connect(self._set_data_1)
        self.tableView_data.set_data_signal.connect(self._set_data_2)

        self.tableView_list.paste.connect(self._paste_1)
        self.tableView_data.paste.connect(self._paste_2)

        self.tableView_list.undo.connect(self._undo)
        self.tableView_list.redo.connect(self._redo)

        self.tableView_data.undo.connect(self._undo)
        self.tableView_data.redo.connect(self._redo)

        self.data_changed = MrSignal()

        self.main_data.data_changed.connect(self._data_changed)

    def _data_changed(self, *args):
        self.data_changed.emit(*args)

    def get_data(self):
        return self.main_data.data

    def clear_data(self):
        self.main_data.data.clear()

    def set_main_data(self, main_data):

        self.main_data.data_changed.disconnect_all()

        self.main_data = main_data
        """:type: fem.utilities.table_data_widget.model.MainData"""

        self.tableView_list.setup_data(self.main_data.headers_1, self.main_data.interface1)
        self.tableView_data.setup_data(self.main_data.headers_2, self.main_data.interface2)

        self.main_data.data_changed.connect(self._data_changed)

    def _open(self, *args):
        filename = getopenfilename(
            caption='Choose Data File',
            directory='',
            filter_=r'.txt (*.txt); .csv (*.csv)'
        )

        if filename in ('', None):
            return

        Action = Actions.ImportAction

        action_data = Action.ActionDataCls(filename)
        action = Action(self.main_data, action_data, self.config)

        command = Commands.ImportCommand(self, action)

        self.config.dispatch((action, action_data, command))

    def _undo(self, *args):
        self.config.dispatch('Undo')

    def _redo(self, *args):
        self.config.dispatch('Redo')

    def _add(self, *args):
        Action = Actions.AddAction

        action_data = Action.ActionDataCls(self.tableView_list.current_row())
        action = Action(self.main_data, action_data)

        command = Commands.AddCommand(self, action)

        self.config.dispatch((action, action_data, command))

    def _insert(self, *args):
        Action = Actions.InsertAction

        action_data = Action.ActionDataCls(self.tableView_list.current_row())
        action = Action(self.main_data, action_data)

        command = Commands.InsertCommand(self, action)

        self.config.dispatch((action, action_data, command))

    def _delete(self, *args):
        Action = Actions.RemoveAction

        action_data = Action.ActionDataCls(self.tableView_list.current_row())
        action = Action(self.main_data, action_data)

        command = Commands.RemoveCommand(self, action)

        self.config.dispatch((action, action_data, command))

    def _set_data_1(self, index, value, role):
        Action = Actions.SetDataAction

        table = self.tableView_list

        index = (table.current_row(), table.current_column())

        action_data = Action.ActionDataCls(index, value)
        action = Action(self.main_data.interface1, action_data)

        command = Commands.SetDataCommand(self, action)

        self.config.dispatch((action, action_data, command))

        return command.command_result

    def _set_data_2(self, index, value, role):
        Action = Actions.SetDataAction

        table = self.tableView_data

        index = (table.current_row(), table.current_column())

        action_data = Action.ActionDataCls(index, value)
        action = Action(self.main_data.interface2, action_data)

        command = Commands.SetDataCommand(self, action)

        self.config.dispatch((action, action_data, command))

        return command.command_result

    def _up(self, *args):
        Action = Actions.UpAction

        table = self.tableView_list

        action_data = Action.ActionDataCls(table.current_row())
        action = Action(self.main_data, action_data)

        command = Commands.UpCommand(self, action)

        self.config.dispatch((action, action_data, command))

    def _down(self, *args):
        Action = Actions.DownAction

        table = self.tableView_list

        action_data = Action.ActionDataCls(table.current_row())
        action = Action(self.main_data, action_data)

        command = Commands.DownCommand(self, action)

        self.config.dispatch((action, action_data, command))

    def _paste_1(self, selection, data):
        Action = Actions.PasteAction

        table = self.tableView_list

        action_data = Action.ActionDataCls(selection, data)
        action = Action(self.main_data.interface1, action_data)

        command = Commands.PasteCommand(self, action, table)

        self.config.dispatch((action, action_data, command))

    def _paste_2(self, selection, data):
        Action = Actions.PasteAction

        table = self.tableView_data

        action_data = Action.ActionDataCls(selection, data)
        action = Action(self.main_data.interface2, action_data)

        command = Commands.PasteCommand(self, action, table)

        self.config.dispatch((action, action_data, command))

    def update_all(self):
        self.tableView_list.update_all()
        self.tableView_data.update_all()

    def _selection_changed(self, row, col):
        self.main_data.interface2.set_index(row)
        self.tableView_data.update_all()
