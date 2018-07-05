"""
dock_table.table_widget

Table widget

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtCore, QtWidgets, QtGui

try:
    from .dock_table_ui import Ui_DockWidget
    from .dock_data_table import DockDataTable
except SystemError:
    from dock_table_ui import Ui_DockWidget
    from dock_data_table import DockDataTable


from fem.utilities.command_dispatcher.action_signal import ActionSignal


class TableWidget(QtWidgets.QDockWidget):
    def __init__(self, *args):
        super(TableWidget, self).__init__(*args)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self._table_view = self.ui.tableView

        self._header = self._table_view.horizontalHeader()
        """:type: QtGui.QHeaderView"""
        self._header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._header.customContextMenuRequested.connect(self._header_context_menu)

        self.ui.pushButton_add.clicked.connect(self._add)
        self.ui.pushButton_delete.clicked.connect(self._remove)
        self.ui.pushButton_insert.clicked.connect(self._insert)
        self.ui.pushButton_up.clicked.connect(self._up)
        self.ui.pushButton_down.clicked.connect(self._down)

        self.add = ActionSignal()
        self.remove = ActionSignal()
        self.insert = ActionSignal()
        self.set_data = ActionSignal()
        self.set_rows = ActionSignal()

        self.up = ActionSignal()
        self.down = ActionSignal()

        self.copy = self._table_view.copy
        self.paste = self._table_view.paste

        self.right_click = self._table_view.right_click

        self._table_view.set_data.connect(self._set_data)

        self._title_bar_widget = self.titleBarWidget()

        self.row_changed = self._table_view.row_changed

    def hide_title_bar(self):
        self.setTitleBarWidget(QtWidgets.QWidget())

    def show_title_bar(self):
        self.setTitleBarWidget(self._title_bar_widget)

    def set_editable_columns(self, int_set):
        assert isinstance(int_set, set)
        self._table_view.set_editable_columns(int_set)

    def _set_data(self, index, value, role):
        row = index.row()
        column = index.column()

        try:
            value = value.toString()
        except AttributeError:
            pass

        self.set_data.emit((row, column), str(value))

        result = self.set_data.results[0]

        self._table_view.update_all()

        # if result is True:
        #     self._table_view.data_changed.emit(row, column)

        return result

    def setup_data(self, data, headers=None):
        self._table_view.setup_data(data, headers)

    # def set_headers(self, headers):
    #     self._table_view.set_headers(headers)

    def _add(self):
        self.add.emit()
        self._table_view.update_all()

    def _remove(self):
        row = self._table_view.current_row()

        if row < 0:
            return

        self.remove.emit(row)

        self._table_view.update_all()

    def _insert(self):
        row = self._table_view.current_row()

        if row < 0:
            row = 0

        self.insert.emit(row)

        self._table_view.update_all()

    def _up(self):
        row = self._table_view.current_row()

        if row < 0:
            row = 0

        self.up.emit(row)

        self._table_view.update_all()

    def _down(self):
        row = self._table_view.current_row()

        if row < 0:
            row = 0

        self.down.emit(row)

        self._table_view.update_all()

    def update_all(self):
        self._table_view.update_all()

    def hide_buttons(self):
        self.ui.pushButton_add.hide()
        self.ui.pushButton_insert.hide()
        self.ui.pushButton_delete.hide()
        self.ui.pushButton_up.hide()
        self.ui.pushButton_down.hide()

    def show_buttons(self):
        self.ui.pushButton_add.show()
        self.ui.pushButton_insert.show()
        self.ui.pushButton_delete.show()
        self.ui.pushButton_up.show()
        self.ui.pushButton_down.show()

    def set_selection(self, selections):
        self._table_view.set_selection(selections)

    def set_focus(self, focus):
        self._table_view.setFocus(focus)

    def select_last_row(self):
        self._table_view.select_last_row()

    def selection(self):
        return self._table_view.selection()

    def current_row(self):
        return self._table_view.current_row()

    def current_column(self):
        return self._table_view.current_column()

    def row_count(self):
        return self._table_view.row_count()

    def column_count(self):
        return self._table_view.column_count()

    def set_table_item_delegate(self, delegate):
        self._table_view.setItemDelegate(delegate)

    def _mouse_release_event(self, event):
        return QtWidgets.QTableView.mouseReleaseEvent(self._table_view, event)

    def _header_context_menu(self, pos):

        # global_pos = self.mapToGlobal(pos)

        rows, ok = QtWidgets.QInputDialog.getText(self, "Enter number of rows.", "Rows:", QtWidgets.QLineEdit.Normal)

        try:
            rows = int(rows)
        except (ValueError, TypeError):
            return

        if ok is False:
            return

        self.set_rows.emit(rows)

    def select_and_edit(self, index):
        self._table_view.select_and_edit(index)

    def select(self, index):
        self._table_view.select(index)
