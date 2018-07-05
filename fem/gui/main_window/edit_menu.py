from __future__ import print_function, absolute_import

from qtpy import QtCore, QtWidgets

from fem.configuration import config


class EditMenu(object):
    def __init__(self, main_window):
        self.main_window = main_window

        self.menu_bar = self.main_window.menuBar()
        """:type: QtWidgets.QMenuBar"""

        self.edit_menu = self.menu_bar.addMenu("&Edit")

        self.actionUndo = self.edit_menu.addAction('Undo')
        self.actionUndo.setShortcut('Ctrl+Z')

        self.actionRedo = self.edit_menu.addAction('Redo')
        self.actionRedo.setShortcut('Ctrl+Shift+Z')

        self.actionUndo.triggered.connect(self._undo)
        self.actionRedo.triggered.connect(self._redo)

        self.config = config
        self.dispatch = self.config.dispatcher.dispatch

    def _undo(self):
        self.dispatch('Undo')

    def _redo(self):
        self.dispatch('Redo')
