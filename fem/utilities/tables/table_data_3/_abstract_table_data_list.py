"""
table_data.table_data_list

table data list

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from ._table_data import TableData, DummyTableData


class AbstractTableDataList(object):
    CheckDataType = DummyTableData
    DefaultDataType = DummyTableData

    def clear(self):
        raise NotImplementedError

    def get_id(self):
        raise NotImplementedError

    @property
    def headers(self):
        raise NotImplementedError
    
    @property
    def formats(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def load_data(self, data):
        raise NotImplementedError

    def add(self, *data):
        raise NotImplementedError

    def remove(self, index):
        raise NotImplementedError

    def add_multiple(self, count, data=None):
        raise NotImplementedError

    def remove_multiple(self, count):
        raise NotImplementedError

    def insert(self, index, *data):
        raise NotImplementedError

    def insert_multiple(self, index, data):
        raise NotImplementedError

    def shape(self):
        raise NotImplementedError

    def editable_columns(self):
        raise NotImplementedError

    def set_data(self, index, value):
        raise NotImplementedError

    def validate(self, *args):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError

    def load(self, data):
        raise NotImplementedError

    def up(self, index):
        raise NotImplementedError

    def down(self, index):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, index):
        raise NotImplementedError

    def __setitem__(self, index, data):
        raise NotImplementedError

    def id_exists(self, id_):
        raise NotImplementedError

    def subdata(self, index):
        raise NotImplementedError

    def has_subdata(self):
        raise NotImplementedError

    def find_index(self, data_id):
        raise NotImplementedError

    def get_index(self, data):
        raise NotImplementedError

    def ids(self):
        raise NotImplementedError

    @property
    def size(self):
        raise NotImplementedError
