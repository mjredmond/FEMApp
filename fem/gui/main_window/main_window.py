from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtCore

from fem.configuration import config
from .beta_menu import BetaMenu
from .edit_menu import EditMenu
from .file_menu import FileMenu
from .help_menu import HelpMenu
from .logging_dock import LoggingDock
from .view_menu import ViewMenu
from ... import actions
from ...gui.vtk_widget import VTKWidget
from ...model import Model
from ...plugins import Plugins


# do not remove below


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)

        self._model = Model()

        self.config = config

        self.config.register_main_window(self)
        self.config.register_main_data(self._model)

        self.logging_dock = LoggingDock(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logging_dock)

        self.file_menu = FileMenu(self)
        self.edit_menu = EditMenu(self)
        self.view_menu = ViewMenu(self)
        self.help_menu = HelpMenu(self)
        self.beta_menu = BetaMenu(self)

        self.config.dispatcher.undo_stack.cleanChanged.connect(self._clean_changed)

        self.update_window_title()

        self.vtk_widget = VTKWidget(self)

        self._current_dock = None

        self.plugins = Plugins(self)

    def update_all(self):
        self.vtk_widget.groups_toolbar.update_all()

    def update_window_title(self):
        self.setWindowTitle(self.config.window_title())

    def _before_close(self):
        self.save_settings()

        self.vtk_widget.finalize()
        self.vtk_widget = None

        self.plugins.finalize()
        self.plugins = None

    def show(self):
        super(MainWindow, self).show()
        QtWidgets.QApplication.instance().processEvents()
        self.vtk_widget.initialize()

    def show_dock(self, dock):
        if self._current_dock is None:
            self._current_dock = dock
            return

        if dock is not self._current_dock:
            self._current_dock.hide()

        self._current_dock = dock

    def current_dock(self):
        return self._current_dock

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

    def get_model(self):
        return self._model

    def sizeHint(self):
        return QtCore.QSize(1800, 1200)

    def closeEvent(self, event, *args, **kwargs):
        if not self.file_menu.check_on_close():
            event.ignore()
            return

        self._before_close()

        super(MainWindow, self).closeEvent(event, *args, **kwargs)

    def _clean_changed(self, is_clean):
        self.update_window_title()


