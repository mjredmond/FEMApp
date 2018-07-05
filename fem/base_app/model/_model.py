from __future__ import print_function, absolute_import

from fem.utilities import BaseObject


class BaseModel(BaseObject):
    def __init__(self):
        pass

    def clear(self):
        raise NotImplementedError

    def set_data(self, data):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError

    def read_from_file(self, filename):
        raise NotImplementedError

    def validation_data(self, data, index):
        raise NotImplementedError

    def validation_data_2(self, data, index1, index2):
        raise NotImplementedError

    def save_to_file(self, filename):
        raise NotImplementedError

    @classmethod
    def copy_cls(cls):
        class _Tmp(cls):
            pass

        _Tmp.__name__ = cls.__name__

        return _Tmp
