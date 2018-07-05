"""
fem.utilities.tables.abstract_table._abstract_table

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six.moves import range

from qtpy import QtCore, QtWidgets, QtGui

from fem.utilities import MrSignal

from operator import itemgetter

import numpy as np


class EmptyTable(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super(EmptyTable, self).__init__(parent, *args)

        self.setLayout(QtWidgets.QVBoxLayout())

        #### buttons ####

        self.pushButton_add = QtWidgets.QPushButton('Add', self)
        self.pushButton_insert = QtWidgets.QPushButton('Insert', self)
        self.pushButton_delete = QtWidgets.QPushButton('Delete', self)

        self.button_spacer = QtWidgets.QSpacerItem(
            100, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        self.button_layout = QtWidgets.QHBoxLayout()

        self.button_layout.addWidget(self.pushButton_add)
        self.button_layout.addWidget(self.pushButton_insert)
        self.button_layout.addWidget(self.pushButton_delete)

        self.button_layout.addItem(self.button_spacer)

        #### table_2 ####

        self.table = QtWidgets.QTableView(self)
        self.table.wheelEvent = self._wheel_event
        self.table.resizeRowsToContents = self._resize_rows
        self.table.resizeColumnsToContents = self._resize_columns
        # self.table_2.setModel(QtCore.QAbstractTableModel())

        #### bottom buttons ####

        self.pushButton_up = QtWidgets.QPushButton('^', self)
        self.pushButton_down = QtWidgets.QPushButton('v', self)

        self.lineEdit_rows = QtWidgets.QLineEdit(self)
        self.lineEdit_rows.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_rows.setCursor(QtCore.Qt.ArrowCursor)
        self.lineEdit_rows.setMaximumWidth(50)

        self.lineEdit_rows.editingFinished.connect(self._set_rows)
        self.lineEdit_rows.mousePressEvent = self._rows_mouse_press

        self.lineEdit_rows.setStyleSheet(
            """
            QLineEdit::hover{
            background-color: Lightcyan
            }
            """
        )

        self.bottom_spacer = QtWidgets.QSpacerItem(
            100, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        self.bottom_layout = QtWidgets.QHBoxLayout()

        self.bottom_layout.addWidget(self.pushButton_up)
        self.bottom_layout.addWidget(self.pushButton_down)
        self.bottom_layout.addItem(self.bottom_spacer)
        self.bottom_layout.addWidget(self.lineEdit_rows)

        #### add to layout ####

        self.layout().addItem(self.button_layout)
        self.layout().addWidget(self.table)
        self.layout().addItem(self.bottom_layout)

        # self.table_2.selectionModel().selectionChanged.connect(self._selection_changed)

        self._old_row = -1
        self._old_column = -1

        self._enter_down = False

        self.selection_changed = MrSignal()
        self.row_changed = MrSignal()
        self.column_changed = MrSignal()

        self.undo = MrSignal()
        self.redo = MrSignal()
        self.paste = MrSignal()
        self.set_data = MrSignal()
        self.set_rows = MrSignal()
        self.data_changed = MrSignal()

        self.table.keyPressEvent = self._keyPressEvent
        self.table.keyReleaseEvent = self._keyReleaseEvent
        # self.table.mousePressEvent = self._mousePressEvent

        self._scroll_factor = 1.

    def _wheel_event(self, event):

        if not QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier:
            return QtWidgets.QTableView.wheelEvent(self.table, event)

        font = self.table.font()

        new_size = old_size = font.pointSize()

        if event.angleDelta().y() > 0:
            new_size += 1
        else:
            new_size -= 1

        if new_size == 0:
            new_size = old_size

        self._scroll_factor = new_size / old_size

        font.setPointSize(new_size)

        self.table.setFont(font)
        self.table.horizontalHeader().setFont(font)
        self.table.verticalHeader().setFont(font)

        self._resize_rows()
        self._resize_columns()

        self._scroll_factor = 1.

        # return QtWidgets.QTableView.wheelEvent(self.table, event)

    def _resize_rows(self):
        header = self.table.verticalHeader()

        for i in range(self.table.model().rowCount()):
            header.resizeSection(i, self.table.rowHeight(i) * self._scroll_factor)

    def _resize_columns(self):
        header = self.table.horizontalHeader()

        for i in range(self.table.model().columnCount()):
            header.resizeSection(i, self.table.columnWidth(i) * self._scroll_factor)

    def _rows_mouse_press(self, event):
        event.accept()
        self.lineEdit_rows.selectAll()

    def _set_rows(self, *args):
        try:
            rows = int(self.lineEdit_rows.text())
        except (ValueError, TypeError):
            rows = -1

        self.lineEdit_rows.clearFocus()
        self.set_rows.emit(rows)

    def hide_buttons(self):
        self.pushButton_add.hide()
        self.pushButton_insert.hide()
        self.pushButton_delete.hide()
        self.pushButton_up.hide()
        self.pushButton_down.hide()
        self.lineEdit_rows.hide()

    def show_buttons(self):
        self.pushButton_add.show()
        self.pushButton_insert.show()
        self.pushButton_delete.show()
        self.pushButton_up.show()
        self.pushButton_down.show()
        self.lineEdit_rows.show()

    def set_model(self, model):
        self.table.setModel(model)
        self.table.selectionModel().selectionChanged.connect(self._selection_changed)
        self.table.model().dataChanged.connect(self._data_changed)
        
    def set_model_data(self, model_data):
        self.table.model().set_model_data(model_data)

    def _data_changed(self, *args):
        self.data_changed.emit()

    def set_selection(self, selections):
        try:
            QtWidgets.QApplication.instance().focusWidget().clearFocus()
        except AttributeError:
            pass

        selection_model = self.table.selectionModel()

        selection_model.clearSelection()

        first_index = None

        model = self.table.model()

        for i in range(len(selections)):
            selection = selections[i]
            index = model.index(selection[0], selection[1])
            selection_model.select(index, QtCore.QItemSelectionModel.Select)

            if first_index is None:
                first_index = index

        self.table.setFocus()

        return first_index

    def set_selection_and_index(self, selections):
        self.table.setCurrentIndex(self.set_selection(selections))

    def select_last_row(self):
        data_len = self.table.model().rowCount()

        self.set_selection_and_index([[data_len - 1, 0]])

    def select_and_edit(self, row, column):
        index = self.table.model().index(row, column)

        selection_model = self.table.selectionModel()

        selection_model.clear()
        selection_model.select(index, QtCore.QItemSelectionModel.Select)
        self.edit(index)

    def selection_range(self):
        selection = self.table.selectionModel().selectedIndexes()

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

    def selection(self):
        selection = self.table.selectionModel().selectedIndexes()

        tmp = []

        for index in selection:
            row = index.row()
            col = index.column()

            tmp.append((row, col))

        return sorted(tmp, key=itemgetter(0))

    def update_all(self):
        try:
            self.table.model().update_all()
        except AttributeError:
            pass

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
            self.selection_changed.emit((new_row, new_column))

    def _keyPressEvent(self, event):
        QtWidgets.QTableView.keyPressEvent(self.table, event)

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = True
            # event.accept()

        elif event.key() == QtCore.Qt.Key_Tab:
            event.accept()

        if event.matches(QtGui.QKeySequence.Copy):
            self._copy()
            event.accept()

        elif event.matches(QtGui.QKeySequence.Paste):
            paste_data = str(QtWidgets.QApplication.clipboard().text())
            self.paste.emit(self.selection_range(), paste_data)
            event.accept()

        elif event.matches(QtGui.QKeySequence.Undo):
            event.accept()
            self.undo.emit()

        elif event.matches(QtGui.QKeySequence.Redo):
            event.accept()
            self.redo.emit()

    def _keyReleaseEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = False

        QtWidgets.QTableView.keyReleaseEvent(self.table, event)

    def mousePressEvent(self, event):
        self.lineEdit_rows.clearFocus()
        QtWidgets.QWidget.mousePressEvent(self, event)

    def current_index(self):
        index = self.table.currentIndex()
        return index.row(), index.column()

    def _copy(self):
        model = self.table.model()
        selection = self.table.selectionModel().selectedIndexes()

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

    def row_count(self):
        return self.table.model().rowCount()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication([])

    widget = EmptyTable()

    widget.show()

    sys.exit(app.exec_())
