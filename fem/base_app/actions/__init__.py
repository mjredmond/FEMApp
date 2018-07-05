from __future__ import print_function, absolute_import

from .file import (BaseFileCommands, BaseFileActions)


class BaseActions(object):
    BaseFileActions = BaseFileActions

    @classmethod
    def copy_cls(cls):
        class _Tmp(cls):
            BaseFileActions = BaseFileActions.copy_cls()

        _Tmp.__name__ = cls.__name__

        return _Tmp

    @classmethod
    def register_config(cls, BaseConfiguration_):
        cls.BaseFileActions.register_config(BaseConfiguration_)

    @classmethod
    def register_main_data(cls, BaseMainData_):
        cls.BaseFileActions.register_main_data(BaseMainData_)


class BaseCommands(object):
    BaseFileCommands = BaseFileCommands

    @classmethod
    def copy_cls(cls):
        class _Tmp(cls):
            BaseFileCommands = BaseFileCommands.copy_cls()

        _Tmp.__name__ = cls.__name__

        return _Tmp

    @classmethod
    def register_config(cls, BaseConfiguration_):
        cls.BaseFileCommands.register_config(BaseConfiguration_)

    @classmethod
    def register_main_window(cls, BaseMainWindow_):
        cls.BaseFileCommands.register_main_window(BaseMainWindow_)
