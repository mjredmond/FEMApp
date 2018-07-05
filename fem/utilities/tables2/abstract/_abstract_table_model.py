
from qtpy import QtWidgets, QtCore, QtGui

from ._abstract_table_data_list import AbstractTableDataList
from ._abstract_table_data import AbstractTableData

from fem.utilities import MrSignal


class AbstractTableModel(QtCore.QAbstractTableModel):
    
    TableDataList = AbstractTableDataList
    
    def __init__(self, *args):
        super().__init__(*args)
        
        self._data = None
        """:type: AbstractTableDataList"""

        self._editable_columns = None
        """:type: set[int]"""

    def set_model_data(self, data, update_all=True):
        try:
            assert isinstance(data, self.TableDataList)
        except AssertionError:
            print(data.__class__)
            raise

        self._data = data
        
        self._editable_columns = self._data.editable_columns()
        
        if update_all is True:
            self.update_all()

    def set_data_range(self, first_index, data):

        i1, j1 = first_index

        rows = len(data)

        if rows == 0:
            return

        cols = len(data[0])

        _set_data = self._data.set_data

        i_ = i1
        for i in range(rows):
            j_ = j1
            _data_i = data[i]
            for j in range(cols):
                _set_data((i_, j_), _data_i[j])
                j_ += 1
            i_ += 1

        top_left = first_index
        bot_right = first_index[0] + rows - 1, first_index[1] + cols - 1

        self.update_range(top_left, bot_right)

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
            return self._data.get_edit_data_by_index((row, col))

        elif role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return self._data.get_formatted_data_by_index((row, col))

        return None

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if self._data is None:
            return False

        row = index.row()
        col = index.column()

        self._data.set_data((row, col), value)

        return True

    def update_all(self):
        try:
            self._editable_columns = self._data.editable_columns()
        except AttributeError:
            pass

        self.layoutChanged.emit()
        top_left = self.index(0, 0)
        bot_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bot_right)

    def update_range(self, top_left, bot_right):
        try:
            self._editable_columns = self._data.editable_columns()
        except AttributeError:
            pass

        self.layoutChanged.emit()
        top_left = self.index(*top_left)
        bot_right = self.index(*bot_right)
        self.dataChanged.emit(top_left, bot_right)

    def update_row(self, row):
        try:
            self._editable_columns = self._data.editable_columns()
        except AttributeError:
            pass

        self.layoutChanged.emit()
        top_left = self.index(row, 0)
        bot_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bot_right)

    def update_column(self, col):
        try:
            self._editable_columns = self._data.editable_columns()
        except AttributeError:
            pass

        self.layoutChanged.emit()
        top_left = self.index(0, col)
        bot_right = self.index(self.rowCount() - 1, col)
        self.dataChanged.emit(top_left, bot_right)
    
    def resize_data(self, new_size):
        self._data.resize(new_size)
        self.update_all()
    
    def add_data(self):
        self._data.add()
        self.update_all()
    
    def insert_data(self, rows):
        """
        
        :param rows: 
        :type rows: list[int]
        :return: 
        """
        
        self._data.insert_multiple(rows)
        self.update_all()

    def delete_data(self, rows):
        """

        :param rows: 
        :type rows: list[int]
        :return: 
        """

        self._data.remove_multiple(rows)
        self.update_all()
        
    def move_up(self, row):
        self._data.up(row)
        self.update_all()
        
    def move_down(self, row):
        self._data.down(row)
        self.update_all()
        
    def subdata(self, index):
        return self._data.subdata(index)
