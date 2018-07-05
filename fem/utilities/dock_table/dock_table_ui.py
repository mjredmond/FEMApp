# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\redmond\py3libs\mr_dock_table\mr_dock_table_ui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from qtpy import QtCore, QtGui, QtWidgets

try:
    from .dock_data_table import DockDataTable
except SystemError:
    from dock_data_table import DockDataTable


class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(745, 622)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        # self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_add = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_add.setObjectName("pushButton_add")
        self.gridLayout.addWidget(self.pushButton_add, 0, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(602, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 4)
        spacerItem1 = QtWidgets.QSpacerItem(481, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 5, 1, 1)
        self.pushButton_delete = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.gridLayout.addWidget(self.pushButton_delete, 0, 4, 1, 1)
        self.pushButton_insert = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_insert.setObjectName("pushButton_insert")
        self.gridLayout.addWidget(self.pushButton_insert, 0, 3, 1, 1)
        self.pushButton_up = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_up.setMaximumSize(QtCore.QSize(21, 23))
        self.pushButton_up.setObjectName("pushButton_up")
        self.gridLayout.addWidget(self.pushButton_up, 2, 0, 1, 1)
        self.pushButton_down = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_down.setMaximumSize(QtCore.QSize(21, 23))
        self.pushButton_down.setObjectName("pushButton_down")
        self.gridLayout.addWidget(self.pushButton_down, 2, 1, 1, 1)
        self.tableView = DockDataTable(self.dockWidgetContents)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 6)
        DockWidget.setWidget(self.dockWidgetContents)
        self.actionUndo = QtWidgets.QAction(DockWidget)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtWidgets.QAction(DockWidget)
        self.actionRedo.setObjectName("actionRedo")

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "DockWidget"))
        self.pushButton_add.setText(_translate("DockWidget", "Add"))
        self.pushButton_delete.setText(_translate("DockWidget", "Delete"))
        self.pushButton_insert.setText(_translate("DockWidget", "Insert"))
        self.pushButton_up.setText(_translate("DockWidget", "^"))
        self.pushButton_down.setText(_translate("DockWidget", "v"))
        self.actionUndo.setText(_translate("DockWidget", "undo"))
        self.actionUndo.setShortcut(_translate("DockWidget", "Ctrl+Z"))
        self.actionRedo.setText(_translate("DockWidget", "redo"))
        self.actionRedo.setShortcut(_translate("DockWidget", "Ctrl+Shift+Z"))

