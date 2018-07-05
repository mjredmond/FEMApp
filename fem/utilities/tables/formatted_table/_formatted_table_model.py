"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtCore, QtGui

import numpy as np

Qt = QtCore.Qt


class FormattedTableData(object):
    def __init__(self, table_model):

        self.table_model = table_model
        """:type: QtCore.QAbstractTableModel"""

        self.__data = staticmethod(QtCore.QAbstractTableModel.data)

        self._data_roles ={
            Qt.DisplayRole: self._data_display_role,
            Qt.DecorationRole: self._data_decoration_role,
            Qt.EditRole: self._data_edit_role,
            Qt.ToolTipRole: self._data_tooltip_role,
            Qt.StatusTipRole: self._data_statustip_role,
            Qt.WhatsThisRole: self._data_whatsthis_role,
            Qt.SizeHintRole: self._data_sizehint_role,
            Qt.FontRole: self._data_font_role,
            Qt.TextAlignmentRole: self._data_textalignment_role,
            Qt.BackgroundRole: self._data_background_role,
            Qt.ForegroundRole: self._data_foreground_role,
            Qt.CheckStateRole: self._data_checkstate_role,
            Qt.InitialSortOrderRole: self._data_initialsortorder_role,
            Qt.AccessibleTextRole: self._data_accessibletext_role,
            Qt.AccessibleDescriptionRole: self._data_accessibledescription_role
        }

        self.data = np.zeros((0, 0), dtype=object)
        self.data_display_fmt = np.zeros((0, 0), object)
        self.data_edit_fmt = np.zeros((0, 0), object)

        self.data_font = np.zeros((0, 0), dtype=object)
        self.data_alignment = np.zeros((0, 0), dtype=object)
        self.data_background = np.zeros((0, 0), dtype=object)
        self.data_foreground = np.zeros((0, 0), dtype=object)

    def resize(self, rows, columns):
        self.data.resize((rows, columns))
        self.data_display_fmt.resize((rows, columns))
        self.data_edit_fmt.resize((rows, columns))

        self.data_font.resize((rows, columns))
        self.data_alignment.resize((rows, columns))
        self.data_background.resize((rows, columns))
        self.data_foreground.resize((rows, columns))

    def get_data(self, index, role=None):
        return self._data_roles[role](index, role)

    def _data_display_role(self, index, role):
        row, col = index.row(), index.column()
        return self.data_display_fmt[row, col].format(self._data[row, col])

    def _data_decoration_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_edit_role(self, index, role):
        row, col = index.row(), index.column()
        return self.data_edit_fmt[row, col].format(self._data[row, col])

    def _data_tooltip_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_statustip_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_whatsthis_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_sizehint_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_font_role(self, index, role):
        row, col = index.row(), index.column()
        return self.data_font[row, col]

    def _data_textalignment_role(self, index, role):
        row, col = index.row(), index.column()
        return self.data_alignment[row, col]

    def _data_background_role(self, index, role):
        row, col = index.row(), index.column()
        return self.data_background[row, col]

    def _data_foreground_role(self, index, role):
        row, col = index.row(), index.column()
        return self.data_foreground[row, col]

    def _data_checkstate_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_initialsortorder_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_accessibletext_role(self, index, role):
        return self.__data(self.table_model, index, role)

    def _data_accessibledescription_role(self, index, role):
        return self.__data(self.table_model, index, role)


class FormattedTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(FormattedTableModel, self).__init__(parent)

        self._data = FormattedTableData(self)
        self._horizontal_header_data = FormattedTableData(self)
        self._vertical_header_data = FormattedTableData(self)

        self._get_data = self._data.get_data
        self._get_horizontal_header_data = self._horizontal_header_data.get_data
        self._get_vertical_header_data = self._vertical_header_data.get_data

        self._flags_data = np.zeros((0, 0), dtype=object)

    def resize(self, rows, columns):
        self._data.resize(rows, columns)
        self._flags_data.resize((rows, columns))

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self._data.data.shape[0]

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self._data.data.shape[1]

    def data(self, index, role=None):
        return self._get_data(index, role)

    def headerData(self, index, orientation, role=None):
        if orientation == Qt.Horizontal:
            return self._get_horizontal_header_data(index, role)
        else:
            return self._get_vertical_header_data(index, role)

    def flags(self, index):
        row, col = index.row(), index.column()
        return self._flags_data[row, col]


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication([])

    db = QtGui.QFontDatabase()

    combo = QtWidgets.QComboBox()

    families = db.families()

    for i in range(len(families)):
        family = families[i]
        combo.addItem(family)
        combo.setItemData(i, family, Qt.FontRole)

    combo.show()

    sys.exit(app.exec_())

