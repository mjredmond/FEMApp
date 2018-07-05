from __future__ import print_function, absolute_import

from fem.configuration import config


class ViewMenu(object):
    def __init__(self, main_window):
        self.main_window = main_window

        self.menu_bar = self.main_window.menuBar()
        """:type: QtWidgets.QMenuBar"""

        self.view_menu = self.menu_bar.addMenu("&View")

        self.config = config
        self.dispatch = self.config.dispatcher.dispatch
