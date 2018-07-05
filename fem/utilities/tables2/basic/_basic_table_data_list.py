from ..abstract import AbstractTableDataList

from ._basic_table_data import DummyTableData

from fem.utilities import MrSignal

from ...error_handling import MyExceptions


class BasicTableDataList(AbstractTableDataList):
    CheckDataType = DummyTableData
    DefaultDataType = DummyTableData

    def __init__(self, data_id=None):
        super().__init__()

        from ._basic_multi_table_widget import BasicMultiTableWidget
        self.MultiTableWidget = BasicMultiTableWidget
        
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

    def _register_data(self, data):
        data.register_model(self.model)
        data.register_parent(self)

    def add(self, *data):

        if len(data) > 0 and isinstance(data[0], self.CheckDataType):
            tmp = data[0]
        else:
            tmp = self.DefaultDataType()

        # object needs to be added to data first for logging purposes
        self.data.append(tmp)
        
        # this should ALWAYS be registered here, so some stuff needs to be recoded
        self._register_data(tmp)

        if len(data) > 0:
            tmp.load(data)

        self.list_changed.emit()

        del self._ids[:]

        return tmp

    def remove(self, index):
        try:
            tmp = self.data[index]
            del self.data[index]
        except MyExceptions.IndexError:
            return None

        self.list_changed.emit()

        return tmp

    def remove_multiple(self, indices):
        offset = 1
        for i in range(1, len(indices)):
            indices[i] -= offset
            offset += 1

        for i in indices:
            self.remove(i)

    def insert(self, index, *data):

        if len(data) > 0 and isinstance(data[0], self.CheckDataType):
            tmp = data[0]
        else:
            tmp = self.DefaultDataType()

        if index < 0:
            index = 0

        try:
            self.data.insert(index, tmp)
            if len(data) > 0:
                tmp.load(data)
            self._register_data(tmp)
            del self._ids[:]
            self.list_changed.emit()
        except MyExceptions.IndexError:
            tmp = None

        return tmp

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
        is_valid, value = self.validate(index, value)
        
        if is_valid is True:
            row, col = index
            # data = self.data[row]
            self.data[row].set_data(col, value)

    def validate(self, index, value):
        return True, value

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

    def __setitem__(self, index, data):
        assert isinstance(data, self.CheckDataType)
        # TODO: what to do here?
        self.data[index] = data

    def id_exists(self, id_):
        for data_i in self.data:
            if data_i.get_id() == id_:
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
                if data[i].get_id() == data_id:
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
    
    # TODO: remove
    def _update_ids(self):
        del self._ids[:]
        _ids = [_.get_id() for _ in self.data]
        self._ids.extend(_ids)
        
    def update_ids(self):
        del self._ids[:]
        _ids = [_.get_id() for _ in self.data]
        self._ids.extend(_ids)

    @property
    def size(self):
        return len(self.data)

    # def get_formatted_data_by_index(self, index):
    #     row, col = index
    #
    #     fmt = self._formats[col]
    #     data = self.data[row][col]
    #
    #     if isinstance(fmt, str):
    #         return fmt % data
    #
    #     return fmt(data)
    #
    # def get_edit_data_by_index(self, index):
    #     row, col = index
    #     return str(self.data[row][col])

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
