# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\redmond\mrFleet\gui\vtk_widget\groups\_groups_ui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from qtpy import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(653, 778)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.dockWidgetContents)
        # self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter_2 = QtWidgets.QSplitter(self.dockWidgetContents)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        # self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 2, 2, 1, 1)
        self.tableView_groups = QtWidgets.QTableView(self.widget)
        self.tableView_groups.setObjectName("tableView_groups")
        self.gridLayout_2.addWidget(self.tableView_groups, 1, 0, 1, 3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_add_group = QtWidgets.QPushButton(self.widget)
        self.pushButton_add_group.setObjectName("pushButton_add_group")
        self.horizontalLayout.addWidget(self.pushButton_add_group)
        self.pushButton_remove_group = QtWidgets.QPushButton(self.widget)
        self.pushButton_remove_group.setObjectName("pushButton_remove_group")
        self.horizontalLayout.addWidget(self.pushButton_remove_group)
        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 2)
        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.widget1 = QtWidgets.QWidget(self.splitter_2)
        self.widget1.setObjectName("widget1")
        self.gridLayout = QtWidgets.QGridLayout(self.widget1)
        # self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 4, 2, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 4, 0, 1, 1)
        self.plainTextEdit_members = QtWidgets.QPlainTextEdit(self.widget1)
        self.plainTextEdit_members.setObjectName("plainTextEdit_members")
        self.gridLayout.addWidget(self.plainTextEdit_members, 1, 0, 1, 3)
        self.label_2 = QtWidgets.QLabel(self.widget1)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)
        self.lineEdit_selection = QtWidgets.QLineEdit(self.widget1)
        self.lineEdit_selection.setObjectName("lineEdit_selection")
        self.gridLayout.addWidget(self.lineEdit_selection, 3, 0, 1, 3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_add_member = QtWidgets.QPushButton(self.widget1)
        self.pushButton_add_member.setObjectName("pushButton_add_member")
        self.horizontalLayout_2.addWidget(self.pushButton_add_member)
        self.pushButton_remove_member = QtWidgets.QPushButton(self.widget1)
        self.pushButton_remove_member.setObjectName("pushButton_remove_member")
        self.horizontalLayout_2.addWidget(self.pushButton_remove_member)
        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.widget1)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.gridLayout_3.addWidget(self.splitter_2, 0, 0, 1, 1)
        self.tableView_groups.raise_()
        self.label_3.raise_()
        self.label_2.raise_()
        self.lineEdit_selection.raise_()
        self.label.raise_()
        self.plainTextEdit_members.raise_()
        self.label.raise_()
        self.label_3.raise_()
        self.frame.raise_()
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "DockWidget"))
        self.pushButton_add_group.setText(_translate("DockWidget", "Add"))
        self.pushButton_remove_group.setText(_translate("DockWidget", "Remove"))
        self.label_3.setText(_translate("DockWidget", "Groups"))
        self.label_2.setText(_translate("DockWidget", "Member List to Add/Remove"))
        self.pushButton_add_member.setText(_translate("DockWidget", "Add"))
        self.pushButton_remove_member.setText(_translate("DockWidget", "Remove"))
        self.label.setText(_translate("DockWidget", "Member List"))

