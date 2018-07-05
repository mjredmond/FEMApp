# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\redmond\mrBaseApp\fem.utilities\table_data_widget\table_data_widget_ui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from qtpy import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(892, 698)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        # self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_add = QtWidgets.QPushButton(self.widget)
        self.pushButton_add.setObjectName("pushButton_add")
        self.horizontalLayout.addWidget(self.pushButton_add)
        self.pushButton_insert = QtWidgets.QPushButton(self.widget)
        self.pushButton_insert.setObjectName("pushButton_insert")
        self.horizontalLayout.addWidget(self.pushButton_insert)
        self.pushButton_delete = QtWidgets.QPushButton(self.widget)
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.horizontalLayout.addWidget(self.pushButton_delete)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.tableView_list = QtWidgets.QTableView(self.widget)
        self.tableView_list.setObjectName("tableView_list")
        self.gridLayout.addWidget(self.tableView_list, 1, 0, 1, 3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_up = QtWidgets.QPushButton(self.widget)
        self.pushButton_up.setMinimumSize(QtCore.QSize(25, 25))
        self.pushButton_up.setMaximumSize(QtCore.QSize(25, 25))
        self.pushButton_up.setObjectName("pushButton_up")
        self.horizontalLayout_2.addWidget(self.pushButton_up)
        self.pushButton_down = QtWidgets.QPushButton(self.widget)
        self.pushButton_down.setMinimumSize(QtCore.QSize(25, 25))
        self.pushButton_down.setMaximumSize(QtCore.QSize(25, 25))
        self.pushButton_down.setObjectName("pushButton_down")
        self.horizontalLayout_2.addWidget(self.pushButton_down)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 1, 1, 1)
        self.widget1 = QtWidgets.QWidget(self.splitter)
        self.widget1.setObjectName("widget1")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget1)
        # self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_open = QtWidgets.QPushButton(self.widget1)
        self.pushButton_open.setObjectName("pushButton_open")
        self.gridLayout_2.addWidget(self.pushButton_open, 0, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 0, 1, 1, 1)
        self.tableView_data = QtWidgets.QTableView(self.widget1)
        self.tableView_data.setObjectName("tableView_data")
        self.gridLayout_2.addWidget(self.tableView_data, 1, 0, 1, 2)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_add.setText(_translate("Form", "Add"))
        self.pushButton_insert.setText(_translate("Form", "Insert"))
        self.pushButton_delete.setText(_translate("Form", "Delete"))
        self.pushButton_up.setText(_translate("Form", "^"))
        self.pushButton_down.setText(_translate("Form", "v"))
        self.pushButton_open.setText(_translate("Form", "Open..."))

