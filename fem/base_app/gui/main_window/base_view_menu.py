from __future__ import print_function, absolute_import

from qtpy import QtCore, QtWidgets

from fem.base_app.configuration import BaseConfiguration
from fem.utilities import BaseObject


class BaseViewMenu(BaseObject):
    BaseConfiguration = BaseConfiguration

    def __init__(self, main_window):
        self.main_window = main_window

        self.menu_bar = self.main_window.menuBar()
        """:type: QtWidgets.QMenuBar"""

        self.view_menu = self.menu_bar.addMenu("&View")

        self.config = self.BaseConfiguration.instance()
        self.dispatch = self.config.dispatcher.dispatch

    @classmethod
    def copy_cls(cls):
        class _Tmp(cls):
            pass

        _Tmp.__name__ = cls.__name__

        return _Tmp
