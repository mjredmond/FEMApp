"""
table_data.table_data_list

table data list

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities import MrSignal
from fem.utilities.debug import show_caller
from fem.utilities.error_handling import MyExceptions
from fem.utilities.tables2.abstract._abstract_table_data_list import AbstractTableDataList
from ._table_data import DummyTableData


class TableDataList(AbstractTableDataList):
    CheckDataType = DummyTableData
    DefaultDataType = DummyTableData

    def __init__(self, data_id=None):
        self.data = []
        """:type: list[DummyTableData]"""

        self._headers = list(self.DefaultDataType.headers)
        self._formats = list(self.DefaultDataType.formats)
        self._setters = list(self.DefaultDataType.setters)

        self._data_id = data_id

        self.list_changed = MrSignal()

        self._ids = []

    def clear(self):
        try:
            self.data.clear()
        except AttributeError:
            del self.data[:]

        del self._ids[:]

    def get_id(self):
        return self._data_id

    @property
    def headers(self):
        return self._headers

    @property
    def formats(self):
        return self._formats
    
    @property
    def setters(self):
        return self._setters

    def get_data(self):
        return list(self.data)

    def load_data(self, data):
        del self.data[:]
        self.data.extend(list(data))
        self._update_ids()

    def add(self, *data):
        tmp = self.DefaultDataType()

        # object needs to be added to data first for logging purposes
        self.data.append(tmp)

        if len(data) > 0:
            tmp.load(data)

        self.list_changed.emit()

        del self._ids[:]

    def remove(self, index):
        try:
            tmp = self.data[index]
            del self.data[index]
        except MyExceptions.IndexError:
            return None

        self.list_changed.emit()

    def remove_multiple(self, indices):
        offset = 1
        for i in range(1, len(indices)):
            indices[i] -= offset
            offset += 1
            
        for i in indices:
            self.remove(i)

    def insert(self, index, *data):
        tmp = self.DefaultDataType()

        if index < 0:
            index = 0

        try:
            self.data.insert(index, tmp)
            if len(data) > 0:
                tmp.load(data)
            del self._ids[:]
            self.list_changed.emit()
        except MyExceptions.IndexError:
            pass
    
    def insert_multiple(self, indices):
        """
        
        :param indices: 
        :type indices: list[int]
        :return: 
        """
        
        if len(indices) == 0:
            return
        
        offset = 1
        for i in range(1, len(indices)):
            indices[i] += offset
            offset += 1
            
        for i in indices:
            self.insert(i)

    def shape(self):
        return len(self.data), len(self.headers)

    def editable_columns(self):
        return set(range(len(self.headers)))

    def set_data(self, index, value):
        row, column = index
        
        try:
            data = self.data[row]
        except MyExceptions.IndexError:
            print('index error')
            return
        
        getattr(data, self._setters[column])(value)

    def validate(self, *args):
        raise NotImplementedError

    def serialize(self):
        data = []

        for data_i in self.data:
            data.append(data_i.serialize())

        return data

    def load(self, data):
        self.list_changed.block()

        for data_i in data:
            self.add(data_i)

        self.list_changed.unblock()

        del self._ids[:]

        # self._update_ids()

        # make sure to update other data if needed

    def _move(self, i1, i2):
        self.data[i1], self.data[i2] = self.data[i2], self.data[i1]
        del self._ids[:]
        self.list_changed.emit()

    def up(self, index):
        if index <= 0 or index >= len(self.data):
            return False

        i1 = index
        i2 = index - 1

        self._move(i1, i2)

        return True

    def down(self, index):
        if index < 0 or index >= len(self.data) - 1:
            return False

        i1 = index
        i2 = index + 1

        self._move(i1, i2)

        return True

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        if isinstance(index, str):
            if index == '':
                return None
            index = self.ids().index(index)
        return self.data[index]

    @show_caller
    def __setitem__(self, index, data):
        assert isinstance(data, self.CheckDataType)
        # TODO: what to do here?
        self.data[index] = data

    def id_exists(self, id_):
        for data_i in self.data:
            if data_i.id == id_:
                return True

        return False

    def subdata(self, index):
        row, column = index
        try:
            return self.data[row].subdata(column)
        except (AttributeError, IndexError):
            return None

    def has_subdata(self):
        try:
            data = self.data[0]
        except IndexError:
            return None
        except KeyError:
            raise KeyError(self._data_id)

        for i in range(len(data)):
            try:
                subdata = data.subdata(i)
                if subdata is not None:
                    return subdata
            except NotImplementedError:
                pass

        return None

    def find_index(self, data_id):
        if isinstance(data_id, str):
            data = self.data
            for i in range(len(data)):
                if data[i].id == data_id:
                    return i
        elif isinstance(data_id, self.CheckDataType):
            data = self.data
            for i in range(len(data)):
                if data_id is data[i]:
                    return i
        return -1

    def get_index(self, data):
        return data

    def ids(self):
        if len(self._ids) == 0:
            self._update_ids()

        return list(self._ids)

    def _update_ids(self):
        del self._ids[:]

        _ids = self._ids

        for data in self.data:
            _ids.append(data.id)

    @property
    def size(self):
        return len(self.data)

    def get_formatted_data_by_index(self, index):
        row, col = index

        return self._formats[col] % self.data[row][col]

    def get_edit_data_by_index(self, index):
        row, col = index
        return str(self.data[row][col])
    
    def resize(self, new_size):
        data_len = len(self.data)
        
        if data_len == new_size:
            return
        
        if new_size > data_len:
            diff = new_size - data_len
            
            for i in range(diff):
                self.add()
                
        else:
            diff = data_len - new_size
            
            last_i = data_len - 1
            
            for i in range(diff):
                self.remove(last_i)
                last_i -= 1
    