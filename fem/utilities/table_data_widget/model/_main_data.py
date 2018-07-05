"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities import BaseObject, MrSignal

from collections import OrderedDict
import numpy as np

from six.moves import range
from six import iteritems


def new_name(data, name):
    if name is None:
        name = 'Data'

    if name not in data:
        return name

    i = 0

    while True:
        i += 1
        name_ = '%s_%d' % (name, i)
        if name_ not in data:
            return name_

    raise Exception('Should never get here!!')


class MainDataInterface1(object):
    def __init__(self, main_data):
        self.main_data = main_data
        """:type: MainData"""

        self._data = self.main_data.data
        self._data_keys = self.main_data.data_keys

    def set_main_data(self, main_data):
        self.main_data = main_data
        self._data = self.main_data.data
        self._data_keys = self.main_data.data_keys

    def get_data(self, index):
        row, col = index

        data_key = self._data_keys[row]

        if col == 0:
            return data_key
        elif col == 1:
            return self._data[data_key].shape[0]

    def set_data(self, index, value):
        row, col = index

        if col == 0:
            if value in self.main_data.data:
                return False

            self.main_data.rename(row, value)
        elif col == 1:

            try:
                value = int(value)
            except (ValueError, TypeError):
                return False

            data_key = self._data_keys[row]

            data = self._data[data_key]
            data.resize((value, data.shape[1]), refcheck=False)

        return True

    def shape(self):
        return len(self._data), 2

    def __len__(self):
        return len(self._data)


class MainDataInterface2(object):
    def __init__(self, main_data):
        self.main_data = main_data
        """:type: MainData"""

        self._data = self.main_data.data
        self._data_keys = self.main_data.data_keys

        self._np_data = None

        self._index = 0

    def set_main_data(self, main_data):
        self.main_data = main_data
        self._data = self.main_data.data
        self._data_keys = self.main_data.data_keys

    def set_index(self, index):
        self._index = index
        try:
            data_key = self._data_keys[index]
            self._np_data = self._data[data_key]
        except (IndexError, KeyError):
            self._np_data = None

    def get_data(self, index):
        if self._np_data is None:
            return None

        row, col = index
        return self._np_data[row, col]

    def set_data(self, index, value):
        if self._np_data is None:
            return False

        row, col = index

        try:
            value = float(value)
        except (ValueError, TypeError):
            return False

        try:
            self._np_data[row, col] = value
        except IndexError:
            print(row, col, self._np_data.shape)
            raise

        return True

    def shape(self):
        if self._np_data is None:
            return 0, 0

        return tuple(self._np_data.shape)

    def __len__(self):
        if self._np_data is None:
            return 0

        return self._np_data.shape[0]


class MainData(BaseObject):
    headers_1 = ['Data Id', 'Data Size']
    headers_2 = ['Data']

    def __init__(self):
        super(MainData, self).__init__()

        self.data = OrderedDict()
        self.data_keys = []

        self.interface1 = MainDataInterface1(self)
        self.interface2 = MainDataInterface2(self)

        self.data_changed = MrSignal()

    def _update_keys(self):
        self.data_keys.clear()
        self.data_keys.extend(list(self.data.keys()))

        self.data_changed.emit(list(self.data_keys))

    def rename(self, arg1, new_name_):
        if isinstance(arg1, int):
            old_name = self.data_keys[arg1]
        else:
            old_name = arg1

        old_data = OrderedDict(self.data)

        self.data.clear()

        _data = self.data

        for key, data in iteritems(old_data):
            if old_name == key:
                key = new_name_
            _data[key] = data

        self.data_changed.block()
        self._update_keys()
        self.data_changed.unblock()

        self.data_changed.emit(('rename', old_name, new_name_))

    def add(self, name=None):
        name = new_name(self.data, name)

        self.data[name] = self._new_data()

        self._update_keys()

        self.interface2.set_index(len(self.data) - 1)

    def insert(self, index, name=None, data=None):
        if name in self.data:
            name = new_name(self.data, name)

        old_data = OrderedDict(self.data)

        print('insert', name)

        self.data.clear()

        _data = self.data

        if data is None:
            _new_data = self._new_data()
        else:
            _new_data = data

        found_data = False

        i = 0
        for key, data in iteritems(old_data):
            if i == index:
                _data[name] = _new_data
                found_data = True
            _data[key] = data
            i += 1

        if not found_data:
            _data[name] = _new_data

        self.data_changed.block()
        self._update_keys()
        self.data_changed.unblock()

        self.data_changed.emit(('insert', index, name))

        self.interface2.set_index(index)

    def delete(self, index):
        old_data = OrderedDict(self.data)

        self.data.clear()

        _data = self.data

        index_ = index

        i = -1
        for key, data in iteritems(old_data):
            i += 1
            if i == index:
                continue
            _data[key] = data

        if index >= len(self.data):
            index -= 1

        self.data_changed.block()
        self._update_keys()
        self.data_changed.unblock()

        self.data_changed.emit(('delete', index_))

        self.interface2.set_index(index)

    def up(self, index):
        if index == 0:
            return False

        return self._move(index, index - 1)

    def down(self, index):
        if index == len(self.data) - 1:
            return False

        return self._move(index, index + 1)

    def _move(self, old_index, new_index):
        old_data = OrderedDict(self.data)
        old_keys = list(old_data.keys())

        self.data.clear()

        _data = self.data

        key_old = old_keys[old_index]
        data_old = old_data[key_old]

        key_new = old_keys[new_index]
        data_new = old_data[key_new]

        i = -1
        for key, data in iteritems(old_data):
            i += 1
            if i == new_index:
                _data[key_old] = data_old
                continue
            elif i == old_index:
                _data[key_new] = data_new
                continue
            _data[key] = data

        self._update_keys()

        self.interface2.set_index(new_index)

        return True

    @staticmethod
    def columns():
        return 1

    def _new_data(self):
        return np.zeros((1, self.columns()), dtype=np.float64)

    def __len__(self):
        return len(self.data)

    def serialize(self):
        result = []

        for key, data in iteritems(self.data):
            result.append((key, data.tostring()))

        return result

    def load(self, data):
        tmp = self._new_data()
        dtype = tmp.dtype
        cols = tmp.shape[1]

        for data_ in data:
            key, _data = data_
            tmp = np.fromstring(_data, dtype=dtype)
            self.data[key] = np.array(tmp.reshape((tmp.size // cols, cols)))

        self._update_keys()

    def clear(self):
        self.data.clear()
        self._update_keys()

    def ids(self):
        return list(self.data_keys)


def main_data():
    """

    :return:
    :rtype: MainData
    """

    class _MainData(MainData):
        pass

    _MainData.register(_MainData)
    _MainData.__name__ = MainData.__name__

    return _MainData
