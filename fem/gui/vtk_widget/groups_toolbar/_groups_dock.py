from __future__ import print_function, absolute_import

from qtpy import QtWidgets

from fem.utilities import MrSignal
from ._groups_table_model import GroupsTableModel
from ._groups_ui import Ui_DockWidget
from ..vtk_graphics import VTKGraphics
from ..vtk_graphics.pipelines.picked import PickedSelection

vtk_graphics = VTKGraphics.instance()

fem_groups = vtk_graphics.fem_groups


class GroupsDock(QtWidgets.QDockWidget):
    def __init__(self, main_window):
        super(GroupsDock, self).__init__(main_window)

        self.main_window = main_window

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self._groups_table_model = GroupsTableModel()
        self.ui.tableView_groups.setModel(self._groups_table_model)

        self._groups_selection_model = self.ui.tableView_groups.selectionModel()
        """:type: QtGui.QItemSelectionModel"""

        self._groups_selection_model.selectionChanged.connect(self._groups_selection_changed)

        self.row_changed = MrSignal()
        self.column_changed = MrSignal()
        self.selection_changed = MrSignal()

        self._old_row = -1
        self._old_column = -1

        self.ui.pushButton_add_group.clicked.connect(self.add_group)
        self.ui.pushButton_remove_group.clicked.connect(self.remove_group)

        self.ui.pushButton_add_member.clicked.connect(self.add_members)
        self.ui.pushButton_remove_member.clicked.connect(self.remove_members)

        self._selection = PickedSelection()

        self._selection.data_changed.connect(self._picked_data_changed)

        self.setWindowTitle('Plot/Erase Groups')

    def add_group(self, group_name=None, group_members=None):
        if group_name in (False, None):
            group_name = fem_groups.new_name()

        group = fem_groups.add_group(group_name)

        if group_members is not None:
            group.set_data(group_members)

        self._groups_table_model.update_all()

    def remove_group(self, group):
        if isinstance(group, int):
            group = fem_groups.get_group_by_index(group)
        elif isinstance(group, str):
            group = fem_groups.get_group(group)
        else:
            raise TypeError('GroupsDock.remove_group: group is not an int or string! %s' % str(group))

        fem_groups.remove_group(group.group_name)

        self._groups_table_model.update_all()

    def add_members(self):
        group = self._current_group()

        if group.group_name == 'Default':
            return

        group.add_data(str(self.ui.lineEdit_selection.text()))
        self._update_members_list()

    def remove_members(self):
        group = self._current_group()

        if group.group_name == 'Default':
            return

        group.remove_data(str(self.ui.lineEdit_selection.text()))
        self._update_members_list()

    def show_and_register(self):
        self.show()

        if self._old_row == -1:
            self._groups_row_changed(0)

        from fem.gui.vtk_widget.vtk_graphics.picking import PickingManager

        picking_manager = PickingManager.instance()
        picking_manager.register_selection(self._selection)

        self.main_window.show_dock(self)

    def _groups_selection_changed(self, current, previous):
        """
        :type current: QtGui.QItemSelection
        :type previous:QtGui.QItemSelection
        """

        try:
            first_index = current.indexes()[0]
        except IndexError:
            return

        new_row = first_index.row()
        new_column = first_index.column()

        old_row = self._old_row
        old_column = self._old_column

        selection_changed = False

        if new_row != old_row:
            self._old_row = new_row
            self.row_changed.emit(self._old_row)
            selection_changed = True
            self._groups_row_changed(new_row)

        if new_column != old_column:
            self._old_column = new_column
            self.column_changed.emit(self._old_column)
            selection_changed = True

        if selection_changed:
            self.selection_changed.emit(new_row, new_column)

    def _groups_row_changed(self, row):
        new_group = fem_groups.get_group_by_index(row)

        self.ui.plainTextEdit_members.setPlainText(new_group.to_str())

    def _picked_data_changed(self, *args):
        self.ui.lineEdit_selection.setText(self._selection.to_str())

    def _current_group(self):
        row = self._groups_selection_model.currentIndex().row()
        return fem_groups.get_group_by_index(row)

    def _update_members_list(self):
        group = self._current_group()
        self.ui.plainTextEdit_members.setPlainText(group.to_str())

    def update_all(self):
        self._groups_table_model.update_all()
