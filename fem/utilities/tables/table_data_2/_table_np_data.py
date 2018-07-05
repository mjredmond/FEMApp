"""
table_data.table_data

table data

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from weakref import ref

from ...error_handling import MyExceptions

from ._table_data import TableData


# noinspection PyProtectedMember
class TableNumpyData(TableData):

    dtype = None

    def __init__(self, data_list, index):
        super(TableNumpyData, self).__init__()

        self.data_list = ref(data_list)
        """:type: ref[fem.utilities.tables.table_data._table_np_data_list.TableNumpyDataList]"""

        self.index = index
        """:type: int"""

    def __getitem__(self, index):
        return self.data_list()._data[self.index][index]

    def __setitem__(self, index, value):
        self.data_list()._data[self.index][index] = value

    def __len__(self):
        return self.data_list()._data.shape[1]

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
        return None

    @classmethod
    def columns(cls):
        return len(cls.dtype.names)
