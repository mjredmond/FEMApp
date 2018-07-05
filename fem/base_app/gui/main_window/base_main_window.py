from __future__ import print_function, absolute_import

import os

from qtpy import QtWidgets, QtCore

from fem.base_app.configuration import BaseConfiguration
from fem.base_app.model import BaseModel
from fem.utilities import BaseObject

from .base_file_menu import BaseFileMenu
from .base_edit_menu import BaseEditMenu
from .base_view_menu import BaseViewMenu
from .base_help_menu import BaseHelpMenu
from .base_beta_menu import BaseBetaMenu

from .base_logging_dock import BaseLoggingDock


class BaseMainWindow(QtWidgets.QMainWindow, BaseObject):
    BaseConfiguration = BaseConfiguration

    BaseModel = BaseModel

    BaseFileMenu = BaseFileMenu
    BaseEditMenu = BaseEditMenu
    BaseViewMenu = BaseViewMenu
    BaseHelpMenu = BaseHelpMenu
    BaseBetaMenu = BaseBetaMenu
    BaseLoggingDock = BaseLoggingDock

    def __init__(self, *args):
        super(BaseMainWindow, self).__init__(*args)

        self._main_data = self.BaseModel.instance()

        self.config = self.BaseConfiguration.instance()

        self.config.register_main_window(self)
        self.config.register_main_data(self._main_data)

        self.logging_dock = self.BaseLoggingDock.instance(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logging_dock)

        self.file_menu = self.BaseFileMenu.instance(self)
        self.edit_menu = self.BaseEditMenu.instance(self)
        self.view_menu = self.BaseViewMenu.instance(self)
        self.help_menu = self.BaseHelpMenu.instance(self)
        self.beta_menu = self.BaseBetaMenu.instance(self)

        self.config.dispatcher.undo_stack.cleanChanged.connect(self._clean_changed)

        self.update_window_title()

    def log_text(self):
        return self.logging_dock.log_text()

    def save_settings(self):
        settings_file = self.config.settings_file()

        if settings_file is None:
            return

        settings = QtCore.QSettings(settings_file, QtCore.QSettings.IniFormat)
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())

    def read_settings(self):
        settings_file = self.config.settings_file()

        if settings_file is None or not os.path.isfile(settings_file):
            settings_file = self.config.default_settings_file()

        settings = QtCore.QSettings(settings_file, QtCore.QSettings.IniFormat)
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("windowState"))

    def main_data(self):
        return self._main_data

    def update_all(self):
        raise NotImplementedError

    def update_window_title(self):
        self.setWindowTitle(self.config.window_title())

    def sizeHint(self):
        return QtCore.QSize(1800, 1200)

    def closeEvent(self, event, *args, **kwargs):
        if not self.file_menu.check_on_close():
            event.ignore()
            return

        self._before_close()

        super(BaseMainWindow, self).closeEvent(event, *args, **kwargs)

    def _before_close(self):
        self.save_settings()

    def _clean_changed(self, is_clean):
        self.update_window_title()

    @classmethod
    def copy_cls(cls):
        """

        :return:
        :rtype: BaseMainWindow
        """

        # noinspection PyAbstractClass
        class _Tmp(cls):
            BaseConfiguration = BaseConfiguration.copy_cls()

            BaseMainData = BaseModel.copy_cls()

            BaseFileMenu = BaseFileMenu.copy_cls()
            BaseEditMenu = BaseEditMenu.copy_cls()
            BaseViewMenu = BaseViewMenu.copy_cls()
            BaseHelpMenu = BaseHelpMenu.copy_cls()
            BaseBetaMenu = BaseBetaMenu.copy_cls()
            BaseLoggingDock = BaseLoggingDock.copy_cls()

        _Tmp.BaseFileMenu.BaseConfiguration = _Tmp.BaseConfiguration
        _Tmp.BaseEditMenu.BaseConfiguration = _Tmp.BaseConfiguration
        _Tmp.BaseViewMenu.BaseConfiguration = _Tmp.BaseConfiguration
        _Tmp.BaseHelpMenu.BaseConfiguration = _Tmp.BaseConfiguration
        _Tmp.BaseBetaMenu.BaseConfiguration = _Tmp.BaseConfiguration
        _Tmp.BaseLoggingDock.BaseConfiguration = _Tmp.BaseConfiguration

        _Tmp.__name__ = cls.__name__

        return _Tmp
