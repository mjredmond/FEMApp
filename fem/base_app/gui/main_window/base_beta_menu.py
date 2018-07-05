from __future__ import print_function, absolute_import

import sys
import os.path

from qtpy import QtGui, QtCore, QtWidgets

from fem.base_app.configuration import BaseConfiguration
from fem.utilities import BaseObject


class BaseBetaMenu(BaseObject):
    BaseConfiguration = BaseConfiguration

    def __init__(self, main_window):
        self.main_window = main_window

        self.menu_bar = self.main_window.menuBar()
        """:type: QtWidgets.QMenuBar"""

        self.config = self.BaseConfiguration.instance()

        self.beta_file = self.config.beta_file()

        try:
            self.beta_available = os.path.isfile(self.beta_file) and sys.executable != self.beta_file
        except TypeError:
            self.beta_available = False

        if self.beta_available:
            self.beta_menu = self.menu_bar.addMenu("&Check Beta Release")
            self.beta_version = self.beta_menu.addAction("Beta Release Available!")
            self.beta_version.triggered.connect(self._beta_version)

    def _beta_version(self, *args):
        if not self.beta_available:
            return

        import subprocess

        p = subprocess.Popen([self.beta_file], cwd=os.path.dirname(self.beta_file))
        p.wait()

    @classmethod
    def copy_cls(cls):
        class _Tmp(cls):
            pass

        _Tmp.__name__ = cls.__name__

        return _Tmp
