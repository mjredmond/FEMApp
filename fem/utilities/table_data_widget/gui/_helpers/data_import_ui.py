# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\redmond\fatigue_release_py3\gui\detail_loading\load_import_ui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from qtpy import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(651, 517)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_import = QtWidgets.QPushButton(Form)
        self.pushButton_import.setObjectName("pushButton_import")
        self.gridLayout.addWidget(self.pushButton_import, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(549, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.tableView = QtWidgets.QTableView(Form)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_import.setText(_translate("Form", "Import"))

