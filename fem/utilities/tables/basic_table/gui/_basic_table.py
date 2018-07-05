"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtCore, QtGui

from fem.utilities.tables.empty_table import EmptyTable

from ..model import MainData
from ..configuration import Configuration

from fem.utilities.tables.table_data import TableDataModel
from fem.utilities.debug import show_stack_trace


class BasicTable(QtWidgets.QWidget):
    MainData = MainData
    main_data = None

    def __init__(self, table_id, parent=None, *args):
        super(BasicTable, self).__init__(parent, *args)

        if self.main_data is None:
            self.main_data = self.MainData()
        else:
            self.main_data = self.main_data

        self.config = Configuration(table_id)

        self.dispatcher = self.config.dispatcher

        self.Actions = self.config.Actions
        self.Commands = self.config.Commands
        self.Actions2 = self.config.Actions2
        self.Commands2 = self.config.Commands2

        self.Actions.set_main_data(self.main_data)
        self.Commands.set_main_window(self)
        self.Actions2.set_main_data(self.main_data)
        self.Commands2.set_main_window(self)

        # left table_2

        self.table_1 = EmptyTable(self)

        self.table_1.pushButton_add.clicked.connect(self._add_1)
        self.table_1.pushButton_insert.clicked.connect(self._insert_1)
        self.table_1.pushButton_delete.clicked.connect(self._delete_1)

        self.table_1.pushButton_up.clicked.connect(self._up_1)
        self.table_1.pushButton_down.clicked.connect(self._down_1)

        self.table_model_1 = TableDataModel()
        self.table_1.set_model(self.table_model_1)

        self.table_1.set_data.connect(self._set_data_1)
        self.table_1.paste.connect(self._paste_1)
        self.table_1.set_rows.connect(self._set_rows_1)
        self.table_1.undo.connect(self._undo)
        self.table_1.redo.connect(self._redo)

        self.table_model_1.setup_data(self.main_data)

        # right table_2

        self.table_2 = EmptyTable(self)

        self.table_2.pushButton_add.clicked.connect(self._add_2)
        self.table_2.pushButton_insert.clicked.connect(self._insert_2)
        self.table_2.pushButton_delete.clicked.connect(self._delete_2)

        self.table_2.pushButton_up.clicked.connect(self._up_2)
        self.table_2.pushButton_down.clicked.connect(self._down_2)

        self.table_model_2 = TableDataModel()
        self.table_2.set_model(self.table_model_2)

        self.table_2.set_data.connect(self._set_data_2)
        self.table_2.paste.connect(self._paste_2)
        self.table_2.set_rows.connect(self._set_rows_2)
        self.table_2.undo.connect(self._undo)
        self.table_2.redo.connect(self._redo)

        # self.table_model_2.setup_data(self.main_data)
        # self.table_model_2.set_editable_columns([i for i in range(10)])

        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._splitter.addWidget(self.table_1)
        self._splitter.addWidget(self.table_2)

        self.setLayout(QtWidgets.QHBoxLayout())

        self.layout().addWidget(self._splitter)

        self.table_2.hide()

        #####

        self.table_1.selection_changed.connect(self._selection_1_changed)

    def serialize(self):
        data = []

        for i in range(len(self.main_data)):
            data.append(self.main_data[i].serialize())

    def load(self, data):
        for i in range(len(data)):
            self.main_data.add().load(data[i])

    def clear(self):
        self.main_data.clear()
        self.update_all()

    def set_main_data(self, main_data):
        self.main_data = main_data
        self.Actions.set_main_data(self.main_data)
        self.Actions2.set_main_data(self.main_data)
        self.table_model_1.setup_data(self.main_data)

        self._selection_1_changed(self.table_1.current_index())

        self.update_all()

    def update_all(self):
        self.table_model_1.update_all()
        self.table_model_2.update_all()

        self.table_1.lineEdit_rows.setText(str(self.table_1.table.model().rowCount()))
        self.table_2.lineEdit_rows.setText(str(self.table_2.table.model().rowCount()))

    def _selection_1_changed(self, index):
        subdata = self._subdata(index)
        if subdata is None:
            self.table_2.hide()
            return

        self.table_model_2.setup_data(subdata)
        self.table_2.lineEdit_rows.setText(str(subdata.shape()[0]))
        self.table_2.show()

    ####################################

    def _subdata(self, index=None):
        if index is None:
            index = self._index1()
        return self.main_data.subdata(index)

    def _index1(self):
        r1 = self.table_1.table.currentIndex().row()
        c1 = self.table_1.table.currentIndex().column()

        return r1, c1

    def _index2(self):
        r2 = self.table_2.table.currentIndex().row()
        c2 = self.table_2.table.currentIndex().column()

        return r2, c2

    ####################################

    def _add_1(self):
        Action = self.Actions.AddAction

        action_data = Action.ActionDataCls()

        action = Action(action_data)
        command = self.Commands.AddCommand(action)

        self.config.dispatch(command)

    def _insert_1(self):
        Action = self.Actions.InsertAction

        action_data = Action.ActionDataCls(self._index1())

        action = Action(action_data)
        command = self.Commands.InsertCommand(action)

        self.config.dispatch(command)

    def _delete_1(self):
        Action = self.Actions.RemoveAction

        action_data = Action.ActionDataCls(self.table_1.selection())

        action = Action(action_data)
        command = self.Commands.RemoveCommand(action)

        self.config.dispatch(command)

    def _up_1(self):
        Action = self.Actions.UpAction

        action_data = Action.ActionDataCls(self._index1())

        action = Action(action_data)
        command = self.Commands.UpCommand(action)

        self.config.dispatch(command)

    def _down_1(self):
        Action = self.Actions.DownAction

        action_data = Action.ActionDataCls(self._index1())

        action = Action(action_data)
        command = self.Commands.DownCommand(action)

        self.config.dispatch(command)

    def _set_data_1(self, enter_down, index, value, role):
        Action = self.Actions.SetDataAction

        action_data = Action.ActionDataCls(index, value, enter_down)

        action = Action(action_data)
        command = self.Commands.SetDataCommand(action)

        self.config.dispatch(command)

    def _paste_1(self, selection, data):
        Action = self.Actions.PasteAction

        action_data = Action.ActionDataCls(selection, data)

        action = Action(action_data)
        command = self.Commands.PasteCommand(action)

        self.config.dispatch(command)

    def _set_rows_1(self, rows):
        if rows < 0:
            self.table_1.lineEdit_rows.setText(str(self.table_1.table.model().rowCount()))
            return

        Action = self.Actions.SetRowsAction

        action_data = Action.ActionDataCls(rows)

        action = Action(action_data)
        command = self.Commands.SetRowsCommand(action)

        self.config.dispatch(command)

    ####################################

    def _add_2(self):
        subdata = self._subdata()
        if subdata is None:
            return

        Action = self.Actions2.AddAction

        index1 = self._index1()

        action_data = Action.ActionDataCls(index1)

        action = Action(action_data)
        command = self.Commands2.AddCommand(action)

        self.config.dispatch(command)

    def _insert_2(self):
        subdata = self._subdata()
        if subdata is None:
            return

        index1 = self._index1()
        index2 = self._index2()

        Action = self.Actions2.InsertAction

        action_data = Action.ActionDataCls(index1, index2)

        action = Action(action_data)
        command = self.Commands2.InsertCommand(action)

        self.config.dispatch(command)

    def _delete_2(self):
        subdata = self._subdata()
        if subdata is None:
            return

        index1 = self._index1()

        Action = self.Actions2.RemoveAction

        action_data = Action.ActionDataCls(index1, self.table_2.selection())

        action = Action(action_data)
        command = self.Commands2.RemoveCommand(action)

        self.config.dispatch(command)

    def _up_2(self):
        subdata = self._subdata()
        if subdata is None:
            return

        index1 = self._index1()
        index2 = self._index2()

        Action = self.Actions2.UpAction

        action_data = Action.ActionDataCls(index1, index2)

        action = Action(action_data)
        command = self.Commands2.UpCommand(action)

        self.config.dispatch(command)

    def _down_2(self):
        subdata = self._subdata()
        if subdata is None:
            return

        index1 = self._index1()
        index2 = self._index2()

        Action = self.Actions2.DownAction

        action_data = Action.ActionDataCls(index1, index2)

        action = Action(action_data)
        command = self.Commands2.DownCommand(action)

        self.config.dispatch(command)

    def _set_data_2(self, enter_down, index, value, role):
        Action = self.Actions2.SetDataAction

        action_data = Action.ActionDataCls(self._index1(), index, value, enter_down)

        action = Action(action_data)
        command = self.Commands2.SetDataCommand(action)

        self.config.dispatch(command)

    def _paste_2(self, selection, data):
        Action = self.Actions2.PasteAction

        action_data = Action.ActionDataCls(self._index1(), selection, data)

        action = Action(action_data)
        command = self.Commands2.PasteCommand(action)

        self.config.dispatch(command)

    def _set_rows_2(self, rows):
        if rows < 0:
            self.table_2.lineEdit_rows.setText(str(self.table_2.table.model().rowCount()))
            return

        Action = self.Actions2.SetRowsAction

        action_data = Action.ActionDataCls(self._index1(), rows)

        action = Action(action_data)
        command = self.Commands2.SetRowsCommand(action)

        self.config.dispatch(command)

    #######################

    # @show_stack_trace
    def keyPressEvent(self, event):
        super(BasicTable, self).keyPressEvent(event)

        if event.isAccepted():
            return

        if event.matches(QtGui.QKeySequence.Undo):
            event.accept()
            self._undo()

        elif event.matches(QtGui.QKeySequence.Redo):
            event.accept()
            self._redo()

    #######################

    def _undo(self, *args):
        self.config.dispatch('Undo')

    def _redo(self, *args):
        self.config.dispatch('Redo')
