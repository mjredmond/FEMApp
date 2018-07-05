"""
dock_table.dock_data_table

tbd

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtGui, QtWidgets, QtCore

from fem.utilities import MrSignal

import numpy as np


class ActionData(object):
    def __init__(self, data, extra_data=None, action_name=None):
        assert isinstance(data, tuple)
        self.data = data
        self.extra_data = extra_data
        self.action_name = action_name

    def __repr__(self):
        return 'ActionData(_data_roles=%r, extra_data=%r, action_name=%r)' % (self.data, self.extra_data, self.action_name)

    def __str__(self):
        return '%s%s' % (self.action_name, str(self.data))


class DockDataTableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args):
        super(DockDataTableModel, self).__init__(*args)
        self._headers = None
        self.model_data = None

        self.editable_columns = set()

        self.set_data = MrSignal()

        self._count = 0

    def setup_data(self, data, headers=None):

        if data == []:
            self.model_data = []
            self._headers = []
            return

        if headers is None:
            headers = data.headers

        if not isinstance(headers, (list, tuple)):
            headers = [headers]

        self._headers = headers[:]

        if self._headers[-1] is None:
            del self._headers[-1]

        self.model_data = data

        if self.model_data is None:
            return

        self.update_all()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):

        if role != QtCore.Qt.DisplayRole:
            # if '' is returned, the headers won't show up...
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._headers[section]
            except (TypeError, IndexError):
                return ''
        else:
            return section + 1

    def rowCount(self, index=QtCore.QModelIndex()):
        if self.model_data is None:
            return 0

        return len(self.model_data)

    def columnCount(self, index=QtCore.QModelIndex()):
        if self._headers is None:
            return 0

        return len(self._headers)

    def set_editable_columns(self, int_set):
        self.editable_columns = int_set

    def flags(self, index):
        if int(index.column()) in self.editable_columns:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if self.model_data is None or self._headers is None:
            return ''

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()

            data = self.model_data[row][col]

            if data is None:
                return ''

            return str(data)

        elif role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()

            data = self.model_data[row][col]

            if data is None:
                return ''

            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], float):
                return str([round(i, 6) for i in data])

            return str(data)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if self.model_data is None or self._headers is None:
            return False

        self.set_data.emit(index, value, role)

        return self.set_data.results[0]

    def update_all(self):
        self.layoutChanged.emit()
        top_left = self.index(0, 0)
        bot_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bot_right)


class DockDataTable(QtWidgets.QTableView):

    # row_changed = QtCore.Signal(int)
    # column_changed = QtCore.Signal(int)
    # selection_changed = QtCore.Signal(int, int)

    @classmethod
    def wrap_obj(cls, obj=None, *args, **kwargs):
        """

        :rtype: DockDataTable
        """

        if obj is None:
            obj = cls(*args, **kwargs)
            return obj

        elif isinstance(obj, cls):
            return obj

        assert isinstance(obj, QtWidgets.QTableView)

        obj.__class__ = cls
        # noinspection PyCallByClass,PyTypeChecker
        cls.init(obj)

        return obj

    def __init__(self, *args):
        super(DockDataTable, self).__init__(*args)

        self.table_model = None
        """:type: DockDataTableModel"""

        self.selection_model = None
        """:type: QtGui.QItemSelectionModel"""

        self._old_row = -1
        self._old_column = -1

        self._enter_down = False

        self.set_data = None
        """:type: MrSignal"""

        self.copy = None
        """:type: MrSignal"""
        self.paste = None
        """:type: MrSignal"""
        self.right_click = None
        """:type: MrSignal"""

        self.row_changed = None
        """:type: MrSignal"""
        self.column_changed = None
        """:type: MrSignal"""
        self.selection_changed = None
        """:type: MrSignal"""

        self.init()

    def init(self):
        self.table_model = DockDataTableModel(self)
        self.setModel(self.table_model)

        self.selection_model = self.selectionModel()
        """:type: QtGui.QItemSelectionModel"""
        self.selection_model.selectionChanged.connect(self._selection_changed)

        self._old_row = -1
        self._old_column = -1

        self._enter_down = False

        self.set_data = self.table_model.set_data

        self.copy = MrSignal()
        self.paste = MrSignal()
        self.set_data = self.table_model.set_data
        self.right_click = MrSignal()

        self.row_changed = MrSignal()
        self.column_changed = MrSignal()
        self.selection_changed = MrSignal()

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

        self.setCurrentIndex(first_index)
        # self.setFocus(True)
        self.setFocus()

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
            return

        elif event.matches(QtGui.QKeySequence.Paste):
            paste_data = str(QtWidgets.QApplication.clipboard().text())
            self.paste.emit(self.selection(), paste_data)

        super(DockDataTable, self).keyPressEvent(event)

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

        text = ''

        for i in range(np_data.shape[0]):
            for j in range(np_data.shape[1]):
                text += np_data[i, j] + '\t'
            text += '\n'

        # noinspection PyArgumentList
        clipboard = QtWidgets.QApplication.clipboard()
        """:type: QtGui.QClipboard"""

        # print('text to copy = ', text)
        text = text.replace('\t\n', '\n')[:-1]
        # print('text to copy = ', text)

        clipboard.setText(text)

        # may not be needed
        self.copy.emit(self.selection(), text)

    def keyReleaseEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = False

        super(DockDataTable, self).keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            index = self.indexAt(event.pos())
            self.set_selection([[index.row(), index.column()]])

        super(DockDataTable, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            index = self.indexAt(event.pos())
            self.right_click.emit(index.row(), index.column())

        super(DockDataTable, self).mouseReleaseEvent(event)

    def setup_data(self, data, headers=None):
        self.table_model.setup_data(data, headers)

    def sizeHint(self):
        return QtCore.QSize(800, 500)

    def update_all(self):
        self.table_model.update_all()

    def current_row(self):
        try:
            self.selectionModel().selectedIndices()[0].row()
        except Exception:
            return self._old_row
    
    def current_column(self):
        try:
            self.selectionModel().selectedIndices()[0].column()
        except Exception:
            return self._old_column

    def row_count(self):
        return self.table_model.rowCount()

    def column_count(self):
        return self.table_model.columnCount()

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
        data_len = len(self.table_model.model_data)

        column = self.current_column()

        if column < 0:
            column = 0

        self.set_selection([[data_len - 1, column]])

    def select_and_edit(self, index):
        index = self.table_model.index(*index)
        self.selectionModel().clear()
        self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)
        self.edit(index)

    def select(self, index):
        index = self.table_model.index(*index)
        self.selectionModel().clear()
        self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)
