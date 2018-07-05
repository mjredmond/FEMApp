# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\testing_database\testing_database\utilities\double_tree_ui.ui'
#
# Created: Wed Jun 03 07:40:51 2015
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

# FIXME: change to Qt5 and qtpy
from Qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(863, 353)
        self.gridLayout_2 = QtGui.QGridLayout(Form)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tree1 = QtGui.QTreeView(Form)
        self.tree1.setObjectName(_fromUtf8("tree1"))
        self.horizontalLayout_2.addWidget(self.tree1)
        self.frame = QtGui.QFrame(Form)
        self.frame.setMaximumSize(QtCore.QSize(16777215, 132))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.add_all_btn = QtGui.QPushButton(self.frame)
        self.add_all_btn.setObjectName(_fromUtf8("add_all_btn"))
        self.verticalLayout_3.addWidget(self.add_all_btn)
        self.add_btn = QtGui.QPushButton(self.frame)
        self.add_btn.setObjectName(_fromUtf8("pushButton_add"))
        self.verticalLayout_3.addWidget(self.add_btn)
        self.remove_btn = QtGui.QPushButton(self.frame)
        self.remove_btn.setObjectName(_fromUtf8("remove_btn"))
        self.verticalLayout_3.addWidget(self.remove_btn)
        self.remove_all_btn = QtGui.QPushButton(self.frame)
        self.remove_all_btn.setObjectName(_fromUtf8("remove_all_btn"))
        self.verticalLayout_3.addWidget(self.remove_all_btn)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.frame)
        self.tree2 = QtGui.QTreeView(Form)
        self.tree2.setObjectName(_fromUtf8("tree2"))
        self.horizontalLayout_2.addWidget(self.tree2)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.add_all_btn.setText(_translate("Form", "--->>", None))
        self.add_btn.setText(_translate("Form", "---->", None))
        self.remove_btn.setText(_translate("Form", "<----", None))
        self.remove_all_btn.setText(_translate("Form", "<<---", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

