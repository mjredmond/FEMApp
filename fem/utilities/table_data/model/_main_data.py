"""
fem.utilities.table_data.model._main_data

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities import BaseObject, MrSignal

from .table_data_list import TableDataList


def new_name(data, name):
    if name not in data:
        return name

    i = 0

    while True:
        i += 1
        name_ = '%s_%d' % (name, i)
        if name_ not in data:
            return name_

    raise Exception('Should never get here!!')


class MainData(BaseObject):

    TableDataList = TableDataList
    data_name = 'DataName'

    def __init__(self, data=None):
        super(MainData, self).__init__()

        if data is None:
            self.data = self.TableDataList()
        else:
            self.data = data

    def rename(self, arg1, new_name):
        self.data.rename(arg1, new_name)

    def serialize(self):
        return self.data.serialize()

    def load(self, data):
        self.data.load(data)

    def clear(self):
        self.data.clear()

    def ids(self):
        return self.ids()

    ####################### LEFT TABLE ######################################

    def add(self):
        new_data = self.data.add()
        new_data.id = new_name(self.data.ids(), self.data_name)

    def insert(self, index, name=None, data=None):
        ids = self.data.ids()
        if name in ids:
            name = new_name(ids, name)

        new_data = self.data.insert(index, data)

        if data is None:
            new_data.id = name

    def delete(self, index):
        self.data.remove(index)

    def up(self, index):
        self.data.up(index)

    def down(self, index):
        self.data.down(index)

    @staticmethod
    def columns():
        return len(self.TableDataList.DefaultDataType.headers)

    ####################### RIGHT TABLE ######################################

    def add_2(self, index):
        self.data.add_2(index)

    def insert_2(self, index1, index2, data):
        self.data.insert_2(index1, index2, data)

    def delete_2(self, index1, index2):
        self.data.remove_2(index1, index2)

    def up_2(self, index1, index2):
        self.data.up_2(index1, index2)

    def down_2(self, index1, index2):
        self.data.down_2(index1, index2)

    @staticmethod
    def columns_2():
        return len(self.TableDataList.DefaultDataType.headers_2)
