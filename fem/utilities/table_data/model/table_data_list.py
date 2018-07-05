"""
table_data.table_data_list

table data list

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from .table_data import TableData


class TableDataList(object):
    CheckDataType = TableData
    DefaultDataType = TableData

    headers = []
    headers_2 = []

    def __init__(self):
        self._data = []
        """:type: list[TableData]"""

    def rename(self, arg1, new_name):
        if isinstance(arg1, str):
            ids = self.ids()

            try:
                index = ids.index(arg1)
            except (IndexError, ValueError):
                return

        else:
            index = arg1

        self._data[index].id = new_name

    def get_data(self):
        return list(self._data)

    def load_data(self, ref):
        del self._data[:]
        self._data.extend(list(ref))

    def add(self, data=None):

        if isinstance(data, self.CheckDataType):
            self._data.append(data)
            return data

        if data is not None:
            self._data.append(data)
            return data

        tmp = self.DefaultDataType()

        try:
            self._data.append(tmp)

            if isinstance(data, (list, tuple)):
                tmp.load(data)

            return tmp
        except AttributeError:
            return None

    def remove(self, index):
        try:
            tmp = self._data[index]
            del self._data[index]
            return tmp
        except IndexError:
            return None

    def insert(self, index, data=None):
        if index < 0:
            index = 0

        if data is None or isinstance(data, (tuple, list)):
            data = self.CheckDataType()
        elif not isinstance(data, self.CheckDataType):
            raise ValueError

        if data is None:
            data = self.DefaultDataType()

        try:
            self._data.insert(index, data)
            return data
        except IndexError:
            return None

    def set_data(self, index, value):
        row, column = index

        try:
            old_value = self._data[row][column]
            self._data[row][column] = value
            new_value = self._data[row][column]

            if old_value != new_value:
                return True, old_value, new_value
            else:
                return False, None, None
        except (IndexError, ValueError):
            return False, None, None

    def validate(self, *args):
        raise NotImplementedError

    def get_state(self):
        the_state = []

        data = self._data

        for i in range(len(data)):
            the_state.append(data[i].get_state())

        return tuple(the_state)

    @classmethod
    def compare_states(cls, old_state, new_state):
        # this is only valid for one change at a time

        old_len = len(old_state)
        new_len = len(new_state)

        if old_len < new_len:
            # something added

            for i in range(new_len):
                if new_state[i] != old_state[i]:
                    return ('insert', (i, tuple(new_state[i]))), ('remove', i)

        if old_len > new_len:
            # something removed

            for i in range(old_len):
                if new_state[i] != old_state[i]:
                    return ('remove', i), ('insert', (i, tuple(old_state[i])))

        # _main_data changed
        for i in range(old_len):
            if old_state[i] != new_state[i]:
                return 'set_data', (i, cls._compare_states(old_state[i], new_state[i]))

        return ()

    @staticmethod
    def _compare_states(old_state, new_state):

        difference = []

        assert len(old_state) == len(new_state)

        for i in range(len(old_state)):
            data_id1, data1 = old_state[i]
            data_id2, data2 = new_state[i]

            assert data_id1 == data_id2

            if data1 != data2:
                difference.append((old_state[i], new_state[i]))

        return tuple(difference)

    def set_state(self, row, state):
        self._data[row].set_state(state)

    def serialize(self):
        data = []

        for data_i in self._data:
            data.append(data_i.serialize())

        return data

    def load(self, data):
        for data_i in data:
            self.add().load(data_i)

    def clear(self):
        del self._data[:]

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        if isinstance(index, str):
            index = self.ids().index(index)
        return self._data[index]

    def __setitem__(self, index, data):
        assert isinstance(data, self.CheckDataType)
        # TODO: what to do here?
        self._data[index] = data

    def id_exists(self, id_):
        for data_i in self._data:
            if data_i.id == id_:
                return True

        return False

    def subdata(self, index):
        row, column = index
        return self._data[row].subdata(column)

    def has_subdata(self):
        try:
            data = self._data[0]
        except IndexError:
            return False

        for i in range(len(data)):
            try:
                subdata = data.subdata(i)
                if subdata is not None:
                    return True
            except NotImplementedError:
                pass

        return False

    def find_index(self, data_id):
        if isinstance(data_id, str):
            data = self._data
            for i in range(len(data)):
                if data[i].id == data_id:
                    return i
        elif isinstance(data_id, self.CheckDataType):
            data = self._data
            for i in range(len(data)):
                if data_id is data[i]:
                    return i
        return -1

    def ids(self):
        ids_ = []

        for data in self._data:
            ids_.append(data.id)

        return ids_

    @property
    def size(self):
        return len(self._data)

    def _move(self, index1, index2):
        d1 = self._data[index1]
        d2 = self._data[index2]

        self._data[index1] = d2
        self._data[index2] = d1

    def up(self, index):
        if index <= 0:
            return

        if index >= len(self._data):
            return

        i1 = index
        i2 = index - 1

        self._move(i1, i2)

    def down(self, index):
        if index <= 0:
            return

        if index >= len(self._data) - 1:
            return

        i1 = index
        i2 = index + 1

        self._move(i1, i2)

    ###################################################################################################

    def add_2(self, index):
        row, column = index

        subdata = self._data[row].subdata(column)

        try:
            return subdata.add()
        except IndexError:
            return None

    def remove_2(self, index1, index2):
        r1, c1 = index1
        r2, c2 = index2

        subdata = self._data[r1].subdata(c1)

        try:
            return subdata.remove(r2)
        except IndexError:
            return None

    def insert_2(self, index1, index2, data=None):
        r1, c1 = index1
        r2, c2 = index2

        subdata = self._data[r1].subdata(c1)

        return subdata.insert(r2, data)

    def set_data_2(self, index1, index2, value):
        r1, c1 = index1
        r2, c2 = index2

        subdata = self._data[r1].subdata(c1)

        try:
            old_value = subdata[r2][c2]
            subdata[r2][c2] = value
            new_value = subdata[r2][c2]

            if old_value != new_value:
                return True, old_value, new_value
            else:
                return False, None, None

        except (IndexError, ValueError):
            return False, None, None

    def up_2(self, index1, index2):
        r1, c1 = index1
        r2, c2 = index2

        subdata = self._data[r1].subdata(c1)

        subdata.up(r2)

    def down_2(self, index1, index2):
        r1, c1 = index1
        r2, c2 = index2

        subdata = self._data[r1].subdata(c1)

        subdata.down(r2)
