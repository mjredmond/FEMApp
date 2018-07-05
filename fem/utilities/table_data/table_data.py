"""
table_data.table_data

table data

author: Michael Redmond

"""

from __future__ import print_function, absolute_import


class TableData(object):
    def __getitem__(self, index):
        raise NotImplementedError

    def __setitem__(self, index, value):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def get_state(self):
        raise NotImplementedError

    def set_state(self, state):
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
        raise NotImplementedError

    @staticmethod
    def compare_states(old_state, new_state):
        difference = []

        assert len(old_state) == len(new_state)

        for i in range(len(old_state)):
            data_id1, data1 = old_state[i]
            data_id2, data2 = new_state[i]

            assert data_id1 == data_id2

            if data1 != data2:
                difference.append((old_state[i], new_state[i]))

        return tuple(difference)

    def subdata(self, index):
        raise NotImplementedError
