from __future__ import print_function, absolute_import

__author__ = 'Michael Redmond'

from qtpy import QtCore, QtWidgets, QtGui

from .mr_double_tree_ui import Ui_Form
from .mr_double_tree_handler import MrDoubleTreeHandler


class MrDoubleTree(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MrDoubleTree, self).__init__(parent)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.handler = MrDoubleTreeHandler(self.ui.tree1, self.ui.tree2, self.ui.add_btn, self.ui.remove_btn,
                                           self.ui.add_all_btn, self.ui.remove_all_btn)
