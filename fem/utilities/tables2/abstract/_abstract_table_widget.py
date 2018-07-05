from qtpy import QtCore, QtWidgets, QtGui

from fem.utilities import MrSignal

from operator import itemgetter

import numpy as np

from ._abstract_table_view import AbstractTableView


class AbstractTableWidget(QtWidgets.QWidget):
    
    TableView = AbstractTableView
    
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)

        self.setLayout(QtWidgets.QVBoxLayout())

        #### buttons ####

        self.pushButton_add = QtWidgets.QPushButton('Add', self)
        self.pushButton_insert = QtWidgets.QPushButton('Insert', self)
        self.pushButton_delete = QtWidgets.QPushButton('Delete', self)

        self.pushButton_add.clicked.connect(self._add)
        self.pushButton_insert.clicked.connect(self._insert)
        self.pushButton_delete.clicked.connect(self._delete)

        self.button_spacer = QtWidgets.QSpacerItem(
            100, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        self.button_layout = QtWidgets.QHBoxLayout()

        self.button_layout.addWidget(self.pushButton_add)
        self.button_layout.addWidget(self.pushButton_insert)
        self.button_layout.addWidget(self.pushButton_delete)

        self.button_layout.addItem(self.button_spacer)

        #### tables ####

        self.table = self.TableView(self)

        #### bottom buttons ####

        self.pushButton_up = QtWidgets.QPushButton('^', self)
        self.pushButton_down = QtWidgets.QPushButton('v', self)
        
        self.pushButton_up.clicked.connect(self._up)
        self.pushButton_down.clicked.connect(self._down)

        self.lineEdit_rows = QtWidgets.QLineEdit(self)
        self.lineEdit_rows.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_rows.setCursor(QtCore.Qt.ArrowCursor)
        self.lineEdit_rows.setMaximumWidth(50)

        self.lineEdit_rows.editingFinished.connect(self._set_rows)
        self.lineEdit_rows.mousePressEvent = self._rows_mouse_press

        self.lineEdit_rows.setStyleSheet(
            """
            QLineEdit::hover{
            background-color: Lightcyan
            }
            """
        )

        self.bottom_spacer = QtWidgets.QSpacerItem(
            100, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        self.bottom_layout = QtWidgets.QHBoxLayout()

        self.bottom_layout.addWidget(self.pushButton_up)
        self.bottom_layout.addWidget(self.pushButton_down)
        self.bottom_layout.addItem(self.bottom_spacer)
        self.bottom_layout.addWidget(self.lineEdit_rows)

        #### add to layout ####
        
        self.layout().addItem(self.button_layout)
        self.layout().addWidget(self.table)
        self.layout().addItem(self.bottom_layout)

    def _rows_mouse_press(self, event):
        event.accept()
        self.lineEdit_rows.selectAll()

    def _set_rows(self, *args):
        try:
            rows = int(self.lineEdit_rows.text())
        except (ValueError, TypeError):
            rows = -1

        self.lineEdit_rows.clearFocus()
        self.table.model().resize_data(rows)
        self._update_line_edit()

    def hide_buttons(self):
        self.pushButton_add.hide()
        self.pushButton_insert.hide()
        self.pushButton_delete.hide()
        self.pushButton_up.hide()
        self.pushButton_down.hide()
        self.lineEdit_rows.hide()

    def show_buttons(self):
        self.pushButton_add.show()
        self.pushButton_insert.show()
        self.pushButton_delete.show()
        self.pushButton_up.show()
        self.pushButton_down.show()
        self.lineEdit_rows.show()

    def update_all(self):
        self.table.update_all()
        self._update_line_edit()

    def _update_line_edit(self):
        self.lineEdit_rows.setText(str(self.table.model().rowCount()))

    def row_count(self):
        return self.table.model().rowCount()
    
    def _add(self, *args):
        self.table.model().add_data()
        self._update_line_edit()
        
    def _insert(self, *args):
        selection = self.table.selection()
        
        rows = set([_[0] for _ in selection])
        
        rows = list(sorted(rows))
        
        self.table.model().insert_data(rows)
        self._update_line_edit()

    def _delete(self, *args):
        selection = self.table.selection()

        rows = set([_[0] for _ in selection])

        rows = list(sorted(rows))

        self.table.model().delete_data(rows)
        self._update_line_edit()
        
    def _up(self, *args):
        row = self.table.current_index()[0]
        self.table.model().move_up(row)
        
    def _down(self, *args):
        row = self.table.current_index()[0]
        self.table.model().move_down(row)
        
    def set_model_data(self, data, update_all=True):
        self.table.set_model_data(data, update_all)
        self._update_line_edit()
        
        if data.resizable is True:
            self.show_buttons()
        else:
            self.hide_buttons()
