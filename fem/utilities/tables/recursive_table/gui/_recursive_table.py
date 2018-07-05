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
from fem.utilities import MrSignal


class RecursiveTable(QtWidgets.QWidget):

    def __init__(self, parent=None, main_data=None, *args):
        super(RecursiveTable, self).__init__(parent, *args)

        # FIXME: main_data should be renamed to table_data since it is confusing with app main_data
        self.main_data = main_data

        self.config = Configuration(self.main_data.get_id())

        self.table = EmptyTable(self)

        self.dispatcher = self.config.dispatcher
        self.dispatcher.main_window = self
        self.dispatcher.table = self.table
        self.dispatcher.get_model = self.main_data

        self.Actions = self.config.Actions
        self.Commands = self.config.Commands

        self.Actions.set_main_data(self.main_data)
        self.Commands.set_main_window(self)

        self.table.pushButton_add.clicked.connect(self._add)
        self.table.pushButton_insert.clicked.connect(self._insert)
        self.table.pushButton_delete.clicked.connect(self._delete)

        self.table.pushButton_up.clicked.connect(self._up)
        self.table.pushButton_down.clicked.connect(self._down)

        self.table_model = TableDataModel()
        self.table.set_model(self.table_model)

        self.table.set_data.connect(self._set_data)
        self.table.paste.connect(self._paste)
        self.table.set_rows.connect(self._set_rows)
        self.table.undo.connect(self._undo)
        self.table.redo.connect(self._redo)

        self.table_model.setup_data(self.main_data)

        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._splitter.addWidget(self.table)

        self.setLayout(QtWidgets.QHBoxLayout())

        self.layout().addWidget(self._splitter)

        self.table.selection_changed.connect(self._selection_changed)
        self.table.data_changed.connect(self._data_changed)

        self.subtable = None
        """:type: RecursiveTable"""

        self.data_changed = MrSignal()

    ####################################################################################################################

    def finalize(self):
        self.main_data = None
        self.config = None

        try:
            self.table.setParent(None)
        except RuntimeError:
            pass

        self.table = None

        self.dispatcher = None
        self.Actions = None
        self.Commands = None

        try:
            self.table_model.setParent(None)
        except RuntimeError:
            pass

        self.table_model = None

        try:
            self._splitter.setParent(None)
        except RuntimeError:
            pass

        self._splitter = None

        if self.subtable is not None:
            self.clear_data()

        self.subtable = None

        self.data_changed.disconnect_all()

    def _data_changed(self, *args):
        self.data_changed.emit()

    def _hide_subtable(self):
        if self.subtable is not None:
            # self.subtable.setParent(self)
            self.subtable.hide()

    def _show_subtable(self):
        if self.subtable is not None:
            self._splitter.addWidget(self.subtable)
            self.subtable.show()

    def _subtable(self, subdata):
        if subdata is not None:
            if self.subtable is None:
                self.subtable = RecursiveTable(parent=self, main_data=subdata)
                self.subtable.layout().setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                self.dispatcher.add_child(self.subtable.dispatcher)
                self._splitter.addWidget(self.subtable)
                self.subtable.hide()
                # noinspection PyProtectedMember
                self.subtable.data_changed.connect(self._data_changed)

            self.subtable.set_main_data(subdata)

        return self.subtable

    def force_update(self, index=None):
        if index is None:
            index = self._index()
        self._selection_changed(index)

    ####################################################################################################################

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

        try:
            self.dispatcher.get_model = main_data
        except AttributeError:
            print(self)
            raise


        self.Actions.set_main_data(self.main_data)
        self.table_model.setup_data(self.main_data)

        self.table.lineEdit_rows.setText(str(self.main_data.shape()[0]))

        self._selection_changed()

        self._update_all()

    def _update_all(self):
        self.table_model.update_all()
        self.table.lineEdit_rows.setText(str(self.table.row_count()))

    def update_all(self):
        self._update_all()

        try:
            self.subtable.update_all()
        except AttributeError:
            pass

    ####################################################################################################################

    def _selection_changed(self, index=None):

        if self.subtable is None:
            self._subtable(self.main_data.has_subdata())

        subdata = self._subdata(index)
        subtable = self._subtable(subdata)

        if None in (subtable, subdata):
            self._hide_subtable()
        else:
            self._show_subtable()

    ####################################################################################################################

    def _subdata(self, index=None):
        if index is None:
            index = self._index()

        return self.main_data.subdata(index)

    def _index(self):
        return self.table.current_index()

    ####################################################################################################################

    def _add(self):
        self.dispatcher.dispatch(('Add', ()))

    def _insert(self):
        self.dispatcher.dispatch(('Insert', (self._index(),)))

    def _delete(self):
        self.dispatcher.dispatch(('Remove', (self.table.selection(),)))

    def _up(self):
        self.dispatcher.dispatch(('Up', (self._index(),)))

    def _down(self):
        self.dispatcher.dispatch(('Down', (self._index(),)))

    def _set_data(self, enter_down, index, value, role):
        self.dispatcher.dispatch(('SetData', (index, value, enter_down)))

    def _paste(self, selection, data):
        self.dispatcher.dispatch(('Paste', (selection, data)))

    def _set_rows(self, rows):
        if rows < 0:
            self.table.lineEdit_rows.setText(str(self.table.table.model().rowCount()))
            return

        self.dispatcher.dispatch(('SetRows', (rows,)))

    def _undo(self, *args):
        self.dispatcher.dispatch('Undo')

    def _redo(self, *args):
        self.dispatcher.dispatch('Redo')

    ####################################################################################################################

    # @show_stack_trace
    def keyPressEvent(self, event):
        super(RecursiveTable, self).keyPressEvent(event)

        if event.isAccepted():
            return

        if event.matches(QtGui.QKeySequence.Undo):
            event.accept()
            self._undo()

        elif event.matches(QtGui.QKeySequence.Redo):
            event.accept()
            self._redo()

    def clear_data(self):

        self.dispatcher.clear_children()

        if self.subtable is not None:
            self.subtable.main_data = None
            self.subtable.hide()
            # # self.subtable.finalize()
            #
            # subtable = self.subtable
            #
            # self.subtable = None
            #
            # try:
            #     subtable.setParent(None)
            # except RuntimeError:
            #     pass

    # def clear_data(self):
    #
    #     self.dispatcher.clear_children()
    #
    #     try:
    #         self.subtable.main_data = None
    #     except AttributeError:
    #         return
    #
    #     self.subtable.clear_data()
    #     self._hide_subtable()
    #     self.subtable.setParent(None)
    #     self.subtable = None
