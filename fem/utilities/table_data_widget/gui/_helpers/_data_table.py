from __future__ import print_function, absolute_import

__author__ = 'Michael Redmond'

from qtpy import QtCore, QtGui, QtWidgets

from fem.utilities import MrSignal

import numpy as np


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, *args):
        super(TableModel, self).__init__(*args)
        self.headers = None
        self._data = None
        self._get_data = None
        self._set_data = None

        self.editable_columns = set()

        self.data_changed = MrSignal()

        self.set_data_signal = MrSignal()

    def set_headers(self, headers):
        self.headers = headers
        self.update_all()

    def setup_data(self, headers, data):

        if not isinstance(headers, (list, tuple)):
            headers = [headers]

        self.headers = headers
        self._data = data
        self._get_data = self._data.get_data
        self._set_data = self._data.set_data

        if headers is None or data is None:
            return

        self.update_all()

    def set_data(self, data):
        self._data = data
        self._get_data = self._data.get_data
        self._set_data = self._data.set_data

        if data is None:
            return

        self.update_all()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if self.headers is not None and role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]
            else:
                return section + 1

        return None

    def rowCount(self, index=QtCore.QModelIndex()):
        if self._data is None:
            return 0

        return len(self._data)

    def columnCount(self, index=QtCore.QModelIndex()):
        if self.headers is None:
            return 0

        return len(self.headers)

    def set_editable_columns(self, int_set):
        self.editable_columns = int_set

    def flags(self, index):
        if int(index.column()) in self.editable_columns:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if self._data is None or self.headers is None:
            return None

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()

            data = self._get_data((row, col))

            if data is None:
                return ''

            return str(data)

        elif role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()

            data = self._get_data((row, col))

            if data is None:
                return ''

            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], float):
                return str([round(i, 6) for i in data])

            return str(data)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if self._data is None or self.headers is None:
            return

        row = index.row()
        col = index.column()

        self.set_data_signal.emit((row, col), str(value), role)

        return self.set_data_signal.results[0]

    def update_all(self):
        self.layoutChanged.emit()
        top_left = self.index(0, 0)
        bot_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bot_right)


class DataTable(QtWidgets.QTableView):

    row_changed = QtCore.Signal(int)
    column_changed = QtCore.Signal(int)
    selection_changed = QtCore.Signal(int, int)

    @classmethod
    def wrap_obj(cls, obj=None, *args, **kwargs):
        """

        :rtype: DataTable
        """

        if obj is None:
            obj = DataTable(*args, **kwargs)
            return obj

        elif isinstance(obj, DataTable):
            return obj

        assert isinstance(obj, QtWidgets.QTableView)

        #parent = obj.parent()

        obj.__class__ = DataTable
        DataTable.init(obj)

        return obj

    def __init__(self, *args):
        super(DataTable, self).__init__(*args)

        self.table_model = None
        """:type: TableModel"""

        self.selection_model = None
        """:type: QtGui.QItemSelectionModel"""
        #self.selection_model.selectionChanged.connect(self._selection_changed)

        self._old_row = -1
        self._old_column = -1

        self._enter_down = False

        self.data_changed = None
        """:type: MrSignal"""

        self.copy = None
        """:type: MrSignal"""

        self.paste = None
        """:type: MrSignal"""

        self.set_data_signal = None
        """:type: MrSignal"""

        self.row_changed = None
        """:type: MrSignal"""

        self.column_changed = None
        """:type: MrSignal"""

        self.selection_changed = None
        """:type: MrSignal"""

        self.undo = None
        """:type: MrSignal"""

        self.redo = None
        """:type: MrSignal"""

        self.init()

    def init(self):
        self.table_model = TableModel(self)
        self.setModel(self.table_model)

        self.selection_model = self.selectionModel()
        """:type: QtGui.QItemSelectionModel"""
        self.selection_model.selectionChanged.connect(self._selection_changed)

        self._old_row = -1
        self._old_column = -1

        self._enter_down = False

        self.data_changed = self.table_model.data_changed

        self.data_changed.connect(self._data_changed)

        self.copy = MrSignal()
        self.paste = MrSignal()

        self.row_changed = MrSignal()
        self.column_changed = MrSignal()
        self.selection_changed = MrSignal()

        self.undo = MrSignal()
        self.redo = MrSignal()

        self.set_data_signal = self.table_model.set_data_signal

        #self.table_model.dataChanged.connect(self._data_updated)

    def _data_changed(self, row, column):
        if self._enter_down:
            row += 1
            column = column

            if row >= self.table_model.rowCount():
                row -= 1

            self.set_selection([[row, column]])

    # def set_selection(self, selections):
    #     try:
    #         QtWidgets.QApplication.instance().focusWidget().clearFocus()
    #     except AttributeError:
    #         pass
    #
    #     self.selection_model.clearSelection()
    #
    #     first_index = None
    #
    #     for i in range(len(selections)):
    #         selection = selections[i]
    #         index = self.table_model.index(selection[0], selection[1])
    #         self.selection_model.select(index, QtCore.QItemSelectionModel.Select)
    #
    #         if first_index is None:
    #             first_index = index
    #
    #     self.setCurrentIndex(first_index)
    #     #self.setFocus(True)
    #     self.setFocus()

    def set_selection(self, selections):
        try:
            QtWidgets.QApplication.instance().focusWidget().clearFocus()
        except AttributeError:
            pass

        self.selection_model.clearSelection()

        first_index = None

        for i in range(len(selections)):
            selection = selections[i]
            index = self.table_model.index(selection[0], selection[1])
            self.selection_model.select(index, QtCore.QItemSelectionModel.Select)

            if first_index is None:
                first_index = index

        #self.setCurrentIndex(first_index)
        self.setFocus(True)
        # self.setFocus()

    def set_selection_and_index(self, selections):
        try:
            QtWidgets.QApplication.instance().focusWidget().clearFocus()
        except AttributeError:
            pass

        self.selection_model.clearSelection()

        first_index = None

        for i in range(len(selections)):
            selection = selections[i]
            index = self.table_model.index(selection[0], selection[1])
            self.selection_model.select(index, QtCore.QItemSelectionModel.Select)

            if first_index is None:
                first_index = index

        self.setCurrentIndex(first_index)
        self.setFocus(True)
        # self.setFocus()

    def selection(self):
        selection = self.selectionModel().selectedIndexes()

        min_row = 9999999
        max_row = -1
        min_col = 9999999
        max_col = -1

        for index in selection:
            row = index.row()
            col = index.column()

            min_row = min(min_row, row)
            max_row = max(max_row, row)

            min_col = min(min_col, col)
            max_col = max(max_col, col)

        return [(min_row, min_col), (max_row, max_col)]

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = True

        elif event.matches(QtGui.QKeySequence.Copy):
            self._copy()

        elif event.matches(QtGui.QKeySequence.Paste):
            paste_data = str(QtWidgets.QApplication.clipboard().text())
            self.paste.emit(self.selection(), paste_data)

        elif event.matches(QtGui.QKeySequence.Undo):
            self.undo.emit()

        elif event.matches(QtGui.QKeySequence.Redo):
            self.redo.emit()

        else:
            super(DataTable, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = False

        super(DataTable, self).keyReleaseEvent(event)

    def setup_data(self, headers, data):
        self.table_model.setup_data(headers, data)

    def set_headers(self, headers):
        self.table_model.set_headers(headers)

    def sizeHint(self):
        return QtCore.QSize(800, 500)

    def update_all(self):
        self.table_model.update_all()

    def current_row(self):
        return self._old_row
    
    def current_column(self):
        return self._old_column

    def set_editable_columns(self, int_set):
        self.table_model.set_editable_columns(int_set)

    def _selection_changed(self, current, previous):
        """
        :type current: QtGui.QItemSelection
        :type previous:QtGui.QItemSelection
        """

        try:
            first_index = current.indexes()[0]
        except IndexError:
            return

        new_row = first_index.row()
        new_column = first_index.column()

        old_row = self._old_row
        old_column = self._old_column

        selection_changed = False

        if new_row != old_row:
            self._old_row = new_row
            self.row_changed.emit(self._old_row)
            selection_changed = True

        if new_column != old_column:
            self._old_column = new_column
            self.column_changed.emit(self._old_column)
            selection_changed = True

        if selection_changed:
            self.selection_changed.emit(new_row, new_column)

    def select_last_row(self):
        data_len = len(self.table_model._data)

        self.set_selection([[data_len-1, 0]])

    def select_and_edit(self, row, column):
        index = self.table_model.index(row, column)
        self.selectionModel().clear()
        self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)
        self.edit(index)

    def _copy(self):
        model = self.model()
        selection = self.selectionModel().selectedIndexes()

        edit_role = QtCore.Qt.EditRole

        try:
            row1 = selection[0].row()
            col1 = selection[0].column()
        except IndexError:
            return

        copy_data = []

        min_row = 9999999
        max_row = -1
        min_col = 9999999
        max_col = -1

        for index in selection:
            row = index.row()
            col = index.column()

            min_row = min(min_row, row)
            max_row = max(max_row, row)

            min_col = min(min_col, col)
            max_col = max(max_col, col)

            data = str(model.data(index, edit_role))

            copy_data.append([row, col, data])

        rows = max_row - min_row + 1
        columns = max_col - min_col + 1

        if rows == 0 or columns == 0:
            return

        np_data = np.zeros((rows, columns), dtype=object)

        for tmp in copy_data:
            row, col, data = tmp

            row -= min_row
            col -= min_col

            np_data[row, col] = data

        text = []

        for i in range(np_data.shape[0]):
            _text = []
            for j in range(np_data.shape[1]):
                _text.append(np_data[i, j])
            text.append('\t'.join(_text))

        text = '\n'.join(text)

        # noinspection PyArgumentList
        clipboard = QtWidgets.QApplication.clipboard()
        """:type: QtGui.QClipboard"""

        clipboard.setText(text)
