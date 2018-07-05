"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtCore, QtGui

from ._table_data_list import TableDataList
from ._table_data import TableData

from fem.utilities import MrSignal


class TableDataModel(QtCore.QAbstractTableModel):

    def __init__(self, *args):
        super(TableDataModel, self).__init__(*args)
        # self._headers = None
        self._data = None
        """:type: fem.utilities.tables.table_data_2._table_data_list.TableDataList"""

        self._editable_columns = None
        """:type: set"""

    def set_model_data(self, data):
        try:
            assert isinstance(data, TableDataList)
        except AssertionError:
            print(data.__class__)
            raise

        self._data = data
        # self._headers = list(data.headers)
        self._editable_columns = self._data.editable_columns()

        self.update_all()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if self._data is not None and role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._data.headers[section]
            else:
                return section + 1

        return None

    def rowCount(self, index=QtCore.QModelIndex()):
        try:
            return len(self._data)
        except TypeError:
            return 0

    def columnCount(self, index=QtCore.QModelIndex()):
        try:
            return len(self._data.headers)
        except (TypeError, AttributeError):
            return 0

    def flags(self, index):
        if int(index.column()) in self._editable_columns:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if self._data is None or not index.isValid():
            return None

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()

            data_ = self._data[row]

            try:
                data = data_.edit_role(col)
            except AttributeError:
                data = data_[col]
            except TypeError:
                data = None

            if data is None:
                return ''

            return str(data)

        elif role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()

            data_ = self._data[row]

            try:
                data = data_[col]
            except (TypeError, IndexError):
                data = None

            if data is None:
                return ''

            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], float):
                return str([round(i, 6) for i in data])
            
            # return self._data.formats[col](data)

            return str(data)

        return None

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if self._data is None:
            return False

        row = index.row()
        col = index.column()
        
        success, old, new = self._data.set_data((row, col), value)

        return success

    def update_all(self):
        try:
            self._editable_columns = self._data.editable_columns()
        except AttributeError:
            pass

        self.layoutChanged.emit()
        top_left = self.index(0, 0)
        bot_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bot_right)
