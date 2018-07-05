"""
table_data.table_data_list

table data list

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from ._table_data import TableData, DummyTableData

from fem.utilities import MrSignal
from fem.utilities.error_handling import MyExceptions
from fem.utilities.debug import debuginfo, show_caller

from ._table_data_list import TableDataList

import numpy as np
import base64
from fem.utilities.zipper import compress, decompress


class TableNumpyDataList(TableDataList):
    CheckDataType = None
    DefaultDataType = None

    def __init__(self, data_id=None):
        super(TableNumpyDataList, self).__init__(data_id)

        self.dtype = self.DefaultDataType.dtype

        self.blank_data = np.zeros(1, dtype=self.dtype)

        self.data = np.zeros(0, dtype=self.dtype)

        self._headers = list(self.data.dtype.names)[:self.DefaultDataType.columns()]

        self.list_changed = MrSignal()

    def clear(self):
        self.data.resize(0)

    def get_data(self):
        return self.data.tolist()

    def load_data(self, data):
        np.copyto(self.data, data)

    def add(self, data=None):

        self.data.resize(self.data.size + 1, refcheck=False)

        if data is not None:
            self.data[-1] = data

        self.list_changed.emit()

        return tuple(self.data[-1])

    def remove(self, index):
        if isinstance(index, (list, tuple)):
            i1 = index[0]
            i2 = index[1]
        else:
            i1 = index
            i2 = index

        indices = list(range(i1, i2 + 1))

        tmp = []

        for i in indices:
            tmp.append(tuple(self.data[i]))

        self.data = np.delete(self.data, indices)

        self.list_changed.emit()

        return tmp

    def insert(self, index, data=None):

        if data is not None:
            assert isinstance(data, tuple)
            try:
                if isinstance(data[0], tuple):
                    return self._insert_multiple(index, data)
            except IndexError:
                data = None

        if index < 0:
            index = 0

        if index >= self.data.size:
            return None

        if data is None:
            data = tuple(self.blank_data[0])

        self.data = np.insert(self.data, index, data)

        self.list_changed.emit()

        return tuple(self.data[index])

    def editable_columns(self):
        return set(range(len(self.headers)))

    def _insert_multiple(self, index, data):
        if index < 0:
            index = 0

        if index >= len(self.data) + 1:
            raise IndexError('%d' % index)

        self.list_changed.block()

        for data_ in data:
            self.data = np.insert(self.data, index, data_)

        self.list_changed.unblock()

        self.list_changed.emit()

        return data

    def serialize(self):
        data_i = self.DefaultDataType(self, 0)

        for i in range(self.data.shape[0]):
            data_i.index = i
            data_i.serialize()

        return base64.b64encode(compress(self.data.tobytes())).decode()

    def load(self, data):
        try:
            self.data = np.fromstring(decompress(base64.b64decode(data.encode())), dtype=self.dtype)
        except ValueError:
            print('get rid of this')
            return

        data_i = self.DefaultDataType(self, 0)

        for i in range(self.data.shape[0]):
            data_i.index = i
            data_i.load(self.data[i])

        # np.copyto(self._data, np.fromstring(base64.b64decode(data.encode()), dtype=self.dtype))

    def __getitem__(self, index):
        if isinstance(index, str):
            index = self.ids().index(index)

        return self.DefaultDataType(self, index)

    def set_data(self, index, value):
        row, column = index

        _data = self.DefaultDataType(self, row)

        try:
            old_value = _data[column]
            _data[column] = value
            new_value = _data[column]

            if old_value != new_value:
                return True, old_value, new_value
            else:
                return False, None, None
        except (MyExceptions.IndexError, MyExceptions.ValueError):
            return False, None, None

    @show_caller
    def __setitem__(self, index, data):
        assert isinstance(data, tuple)

        self.data[index] = data

    def id_exists(self, id_):

        data_i = self.DefaultDataType(self, 0)

        for i in range(self.data.shape[0]):
            data_i.index = i
            if data_i.id == id_:
                return True

        return False

    def subdata(self, index):
        return None

    def has_subdata(self):
        return None

    def find_index(self, data_id):
        assert isinstance(data_id, str)

        data_i = self.DefaultDataType(self, 0)

        for i in range(self.data.shape[0]):
            data_i.index = i
            if data_i.id == data_id:
                return i

        return -1

    def ids(self):

        data_i = self.DefaultDataType(self, 0)

        ids_ = []

        for i in range(self.data.shape[0]):
            data_i.index = i
            ids_.append(data_i.id)

        return ids_

    def _move(self, i1, i2):
        _data_i1 = tuple(self.data[i1])
        _data_i2 = tuple(self.data[i2])

        self.data[i1], self.data[i2] = _data_i2, _data_i1

        del self._ids[:]

        self.list_changed.emit()

    def shape(self):
        return self.data.shape[0], self.DefaultDataType.columns()

    @property
    def size(self):
        return self.__len__()

    def __len__(self):
        return self.data.shape[0]
