"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range


from qtpy import QtCore, QtWidgets, QtGui

from ._double_tree_handler import DoubleTreeHandler
from ..basic_tree_view import BasicTreeView


class DoubleTree(DoubleTreeHandler, QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.gridLayout_2 = QtWidgets.QGridLayout(self)
        # self.gridLayout_2.setMargin(0)
        # self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName('gridLayout_2')

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName('horizontalLayout_2')

        self.tree1 = BasicTreeView(self)
        self.tree1.setObjectName('tree1')

        self.horizontalLayout_2.addWidget(self.tree1)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setMaximumSize(QtCore.QSize(16777215, 132))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName('frame')

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName('gridLayout')

        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName('verticalLayout_3')

        self.add_all_btn = QtWidgets.QPushButton(self.frame)
        self.add_all_btn.setObjectName('add_all_btn')

        self.verticalLayout_3.addWidget(self.add_all_btn)

        self.add_btn = QtWidgets.QPushButton(self.frame)
        self.add_btn.setObjectName('pushButton_add')

        self.verticalLayout_3.addWidget(self.add_btn)

        self.remove_btn = QtWidgets.QPushButton(self.frame)
        self.remove_btn.setObjectName('remove_btn')

        self.verticalLayout_3.addWidget(self.remove_btn)

        self.remove_all_btn = QtWidgets.QPushButton(self.frame)
        self.remove_all_btn.setObjectName('remove_all_btn')

        self.verticalLayout_3.addWidget(self.remove_all_btn)

        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout_2.addWidget(self.frame)

        self.tree2 = BasicTreeView(self)
        self.tree2.setObjectName('tree2')

        self.horizontalLayout_2.addWidget(self.tree2)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.setWindowTitle('Double Tree')
        self.add_all_btn.setText('--->>')
        self.add_btn.setText('---->')
        self.remove_btn.setText('<----')
        self.remove_all_btn.setText('<<---')

        DoubleTreeHandler.__init__(self, self.tree1, self.tree2, self.add_btn, self.remove_btn,
                                   self.add_all_btn, self.remove_all_btn)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication([])

    double_tree = DoubleTree()
    double_tree.handler.set_data([5, 4, 3, 2, 1], [6, 7, 8, 9])

    double_tree.show()

    sys.exit(app.exec_())

