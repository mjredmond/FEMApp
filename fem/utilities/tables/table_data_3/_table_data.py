"""
table_data.table_data

table data

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from ...error_handling import MyExceptions


class TableData(object):
    headers = []
    formats = []
    setters = []

    def __getitem__(self, index):
        raise NotImplementedError

    def __setitem__(self, index, value):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    @property
    def id(self):
        raise NotImplementedError

    @id.setter
    def id(self, value):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError

    def load(self, data):
        # load from serialization
        raise NotImplementedError

    def subdata(self, index):
        raise NotImplementedError


class DummyTableData(TableData):
    headers = ['col %d' % i for i in range(7)]

    def __init__(self, subdata=True):
        super(DummyTableData, self).__init__()

        self._id = 'Dummy Data'

        self._data = [0, 1, 2, 3, 4, 5, 6]

        self._subdata = []

        if subdata:
            self.init_subdata()

    def init_subdata(self):
        from ._table_data_list import TableDataList
        self._subdata = [None, None, None, TableDataList(), None, None, None]

    def __getitem__(self, index):
        if index == 0:
            return self._id

        return self._data[index - 1]

    def __setitem__(self, index, value):
        if index == 0:
            self._id = value
            return

        self._data[index-1] = value

    def __len__(self):
        return len(self._data) + 1

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def serialize(self):
        return self._id, list(self._data)

    def load(self, data):
        self._id = data[0]

        del self._data[:]
        self._data.extend(data[1])

    def subdata(self, index):
        try:
            tmp = self._subdata[index]
        except MyExceptions.IndexError:
            tmp = None

        return tmp
