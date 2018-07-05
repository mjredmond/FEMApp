from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtGui, QtCore

from ..vtk_graphics import VTKGraphics

vtk_graphics = VTKGraphics.instance()

fem_groups = vtk_graphics.fem_groups


class GroupsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(GroupsTableModel, self).__init__(parent)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):

        if role != QtCore.Qt.DisplayRole:
            # if '' is returned, the headers won't show up...
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return 'Group ID'
            elif section == 1:
                return 'Active'
        else:
            return section + 1

    def rowCount(self, index=None, *args, **kwargs):
        return fem_groups.size()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role in (QtCore.Qt.EditRole, QtCore.Qt.DisplayRole):
            row = index.row()
            col = index.column()

            group = fem_groups.get_group_by_index(row)

            if col == 0:
                return group.group_name
            elif col == 1:
                return group.is_active
            else:
                return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        # FIXME: needs to be done by actions!

        group = fem_groups.get_group_by_index(index.row())

        col = index.column()

        if col == 0:
            fem_groups.rename_group(group.group_name, value)
        elif col == 1:
            group.set_active(value)

        return True

    def update_all(self):
        self.layoutChanged.emit()
        top_left = self.index(0, 0)
        bot_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bot_right)
