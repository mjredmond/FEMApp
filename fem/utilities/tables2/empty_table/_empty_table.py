
from qtpy import QtCore, QtWidgets, QtGui

from operator import itemgetter

from fem.utilities import MrSignal

import numpy as np


class EmptyTable(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self._scroll_factor = 1.
        self._enter_down = True

        self.undo = MrSignal()
        self.redo = MrSignal()

    def setModel(self, model):
        from ..table_data import TableDataModel
        assert isinstance(model, TableDataModel)
        super().setModel(model)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = True

        elif event.key() == QtCore.Qt.Key_Tab:
            event.accept()

        if event.matches(QtGui.QKeySequence.Copy):
            self._copy()
            event.accept()

        elif event.matches(QtGui.QKeySequence.Paste):
            paste_data = str(QtWidgets.QApplication.clipboard().text())
            self.model().set_data_range(self.selection_range(), paste_data)
            event.accept()

        elif event.matches(QtGui.QKeySequence.Undo):
            event.accept()
            self.undo.emit()

        elif event.matches(QtGui.QKeySequence.Redo):
            event.accept()
            self.redo.emit()

    def keyReleaseEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = False
        super().keyReleaseEvent(event)

    def wheelEvent(self, event):
        if not QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier:
            return super().wheelEvent(event)

        font = self.font()

        new_size = old_size = font.pointSize()

        if event.angleDelta().y() > 0:
            new_size += 1
        else:
            new_size -= 1

        if new_size == 0:
            new_size = old_size

        self._scroll_factor = new_size / old_size

        font.setPointSize(new_size)

        self.setFont(font)
        self.horizontalHeader().setFont(font)
        self.verticalHeader().setFont(font)

        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        self._scroll_factor = 1.

    def resizeRowsToContents(self):
        header = self.verticalHeader()

        for i in range(self.model().rowCount()):
            header.resizeSection(i, self.rowHeight(i) * self._scroll_factor)

    def resizeColumnsToContents(self):
        header = self.horizontalHeader()

        for i in range(self.model().columnCount()):
            header.resizeSection(i, self.columnWidth(i) * self._scroll_factor)

    def set_selection(self, selections):
        try:
            QtWidgets.QApplication.instance().focusWidget().clearFocus()
        except AttributeError:
            pass

        selection_model = self.selectionModel()

        selection_model.clearSelection()

        first_index = None

        model = self.model()

        for i in range(len(selections)):
            selection = selections[i]
            index = model.index(selection[0], selection[1])
            selection_model.select(index, QtCore.QItemSelectionModel.Select)

            if first_index is None:
                first_index = index

        self.setFocus()

        return first_index

    def set_selection_and_index(self, selections):
        self.setCurrentIndex(self.set_selection(selections))

    def select_last_row(self):
        data_len = self.model().rowCount()
        self.set_selection_and_index([[data_len - 1, 0]])

    def select_and_edit(self, row, column):
        index = self.model().index(row, column)

        selection_model = self.selectionModel()

        selection_model.clear()
        selection_model.select(index, QtCore.QItemSelectionModel.Select)

        self.edit(index)

    def selection_range(self):
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

    def selection(self):
        selection = self.selectionModel().selectedIndexes()

        tmp = []

        for index in selection:
            row = index.row()
            col = index.column()

            tmp.append((row, col))

        return sorted(tmp, key=itemgetter(0))

    def update_all(self):
        try:
            self.model().update_all()
        except AttributeError:
            pass

    def current_index(self):
        index = self.currentIndex()
        return index.row(), index.column()

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
