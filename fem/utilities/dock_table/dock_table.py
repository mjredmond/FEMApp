"""
dock_table.dock_table

Dock table

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtCore, QtWidgets, QtGui

from .table_widget import TableWidget

from fem.utilities import MrSignal
from fem.utilities.table_data import TableDataList


class DockTable(QtWidgets.QDockWidget):
    def __init__(self, title1='Table1', title2='Table2', *args):
        super(DockTable, self).__init__(*args)

        self._widget = QtWidgets.QWidget(self)
        self.setWidget(self._widget)

        self._layout = QtWidgets.QGridLayout(self._widget)
        self._widget.setLayout(self._layout)

        self.hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)

        self._layout.addWidget(self.hsplitter)

        self.table1 = TableWidget(self)
        self.table1.setWindowTitle(title1)
        self.table1.hide_title_bar()

        self.table2 = TableWidget(self)
        self.table2.setWindowTitle(title2)
        self.table2.hide_title_bar()

        self.hsplitter.addWidget(self.table1)
        self.hsplitter.addWidget(self.table2)

        self._data = None

        self._title_bar_widget = self.titleBarWidget()

    def hide_title_bar(self):
        self.setTitleBarWidget(QtWidgets.QWidget())

    def show_title_bar(self):
        self.setTitleBarWidget(self._title_bar_widget)

    def _connect_table_2(self):
        self.table1.row_changed.connect(self._update_table2)

    def _disconnect_table_2(self):
        self.table1.row_changed.disconnect(self._update_table2)

    def _update_table2(self, row):

        if row < 0:
            row = 0

        column = self.table1.current_column()

        if column < 0:
            column = 0

        try:
            subdata = self._data.subdata(row, column)
        except NotImplementedError:
            return

        if subdata is None:
            return

        self.table2.setup_data(subdata, self._data.headers_2)
        self.table2.update_all()

    def setup_data(self, data):
        assert isinstance(data, TableDataList)

        self.table1.setup_data(data, data.headers)

        self._data = data

        if data.has_subdata():
            self.table2.show()
            self._connect_table_2()
            self._update_table2(self.table1.current_row())
        else:
            self.table2.hide()
            self._disconnect_table_2()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication([])

    w = DockTable()

    w.show()

    sys.exit(app.exec_())
