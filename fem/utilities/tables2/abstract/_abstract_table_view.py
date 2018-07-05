
from qtpy import QtCore, QtWidgets, QtGui

from operator import itemgetter

from fem.utilities import MrSignal

import numpy as np

from ._abstract_table_model import AbstractTableModel


class AbstractTableView(QtWidgets.QTableView):
    
    TableModel = AbstractTableModel
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self._scroll_factor = 1.
        self._enter_down = False
        self._shift_down = False
        self._ctrl_down = False

        self.undo = MrSignal()
        self.redo = MrSignal()
        
        self._model = self.TableModel()
        self.setModel(self._model)

        self.selection_model = self.selectionModel()
        """:type: QtGui.QItemSelectionModel"""
        self.selection_model.selectionChanged.connect(self._selection_changed)

        self.selection_changed = MrSignal()
        self.row_changed = MrSignal()
        self.column_changed = MrSignal()

        self._old_row = -1
        self._old_column = -1

    def _select_next_row_down(self):
        row, col = self.current_index()

        if row < self.model().rowCount() - 1:
            row += 1

        self.set_selection_and_index([[row, col]])

    def _select_next_row_up(self):
        row, col = self.current_index()

        if row > 0:
            row -= 1

        self.set_selection_and_index([[row, col]])

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._enter_down = True

            if self._ctrl_down is False:
                if self._shift_down is True:
                    self._select_next_row_up()
                else:
                    self._select_next_row_down()

        elif event.key() == QtCore.Qt.Key_Shift:
            self._shift_down = True

        elif event.key() == QtCore.Qt.Key_Control:
            self._ctrl_down = True

        elif event.key() == QtCore.Qt.Key_Tab:
            event.accept()

        if event.matches(QtGui.QKeySequence.Copy):
            self._copy()
            event.accept()

        elif event.matches(QtGui.QKeySequence.Paste):
            
            selection_range = self.selection_range()
            
            paste_data = str(QtWidgets.QApplication.clipboard().text())
            paste_data = _get_paste_data(selection_range, paste_data, 
                                         (self.model().rowCount(), self.model().columnCount())
                                         )
            
            if paste_data is not None:
                self.model().set_data_range(selection_range[0], paste_data)
                top_left = selection_range[0]
                bot_right = selection_range[0][0] + len(paste_data) - 1, selection_range[0][1] + len(paste_data[0]) - 1
                self.set_selection_range(top_left, bot_right)
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

        elif event.key() == QtCore.Qt.Key_Shift:
            self._shift_down = False

        elif event.key() == QtCore.Qt.Key_Control:
            self._ctrl_down = False

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

    def set_selection_range(self, top_left, bot_right):

        selections = []

        rows = bot_right[0] - top_left[0] + 1
        cols = bot_right[1] - top_left[1] + 1

        i_, j_ = top_left

        for i in range(rows):
            for j in range(cols):
                selections.append((i_ + i, j_ + j))

        self.set_selection(selections)

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

        return list(sorted(tmp, key=itemgetter(0)))

    def update_all(self):
        self.model().update_all()

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
    
    def set_model_data(self, data, update_all=True):
        self._model.set_model_data(data, update_all)

    def _selection_changed(self, current, previous):
        """
        :type current: QtGui.QItemSelection
        :type previous: QtGui.QItemSelection
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


def _get_paste_data(selection, data, max_shape=None):
    (row1, col1), (row2, col2) = selection

    selected_row_count = row2 - row1 + 1
    selected_col_count = col2 - col1 + 1

    # noinspection PyTypeChecker
    new_data = str(data)

    if len(new_data) == 0:
        return None
    
    new_data = [_.split('\t') for _ in new_data.split('\n')]

    if len(new_data) == 0:
        return None

    if max_shape is not None:
        paste_rows = min(len(new_data), max_shape[0] - row1)
        paste_cols = min(len(new_data[0]), max_shape[1] - col1)
    else:
        paste_rows = len(new_data)
        paste_cols = len(new_data[0])

    # noinspection PyMissingOrEmptyDocstring
    def get_selection(selected, paste):
        if selected < paste:
            selected = paste

        if selected > paste:
            max_ = selected
            min_ = paste
        else:
            max_ = paste
            min_ = selected

        if max_ % min_ == 0:
            return max_
        else:
            return min_

    selected_row_count = get_selection(selected_row_count, paste_rows)
    selected_col_count = get_selection(selected_col_count, paste_cols)

    repeat_rows = selected_row_count // paste_rows
    repeat_cols = selected_col_count // paste_cols

    a = np.empty((paste_rows, paste_cols), dtype=object)

    for i in range(a.shape[0]):
        a[i] = new_data[i][:paste_cols]

    b = np.concatenate([a] * repeat_rows)
    c = np.concatenate([b] * repeat_cols, axis=1)

    return c.tolist()
