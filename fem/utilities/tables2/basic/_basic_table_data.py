from ..abstract import AbstractTableData

from ...error_handling import MyExceptions


class BasicTableData(AbstractTableData):
    pass


class DummyTableData(BasicTableData):
    headers = ['col %d' % i for i in range(7)]
    formats = ['%s'] * 7
    setters = ['set_%d' % i for i in range(7)]

    def __init__(self, subdata=True):
        super().__init__()

        self._id = ''

        self._data = [0, 1, 2, 3, 4, 5, 6]

        self._subdata = []

        if subdata:
            self.init_subdata()

    def init_subdata(self):
        from ._basic_table_data_list import BasicTableDataList
        self._subdata = [None, None, None, BasicTableDataList(), None, None, None]

    def __getitem__(self, index):
        return self._data[index]

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

    def set_0(self, val):
        self._data[0] = val

    def set_1(self, val):
        self._data[1] = val

    def set_2(self, val):
        self._data[2] = val

    def set_3(self, val):
        self._data[3] = val

    def set_4(self, val):
        self._data[4] = val

    def set_5(self, val):
        self._data[5] = val

    def set_6(self, val):
        self._data[6] = val
