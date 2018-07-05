from __future__ import print_function, absolute_import

from qtpy import QtGui, QtCore, QtWidgets

from ._groups_dock import GroupsDock
from ..gui_helper import GUIPath
from ..vtk_graphics import VTKGraphics

gui_path = GUIPath("groups/images")
vtk_graphics = VTKGraphics.instance()


class GroupsToolbar(QtWidgets.QToolBar):
    def __init__(self, parent):
        super(GroupsToolbar, self).__init__(parent)

        # self.groups_action = self._add_action(QtGui.QIcon(gui_path("groups.png")),
        #                                             "&Plot or Erase", self,
        #                                             statusTip="Plot or erase groups",
        #                                             triggered=self.groups_plot)

        self.groups_action = QtWidgets.QAction('Groups', self)
        self.groups_action.triggered.connect(self.groups_plot)
        self.addAction(self.groups_action)

        self.setIconSize(QtCore.QSize(32, 32))

        self.groups_dock = GroupsDock(parent)

        parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.groups_dock)

        self.groups_dock.hide()

    def _add_action(self, *args, **kwargs):
        action = QtWidgets.QAction(*args, **kwargs)
        #action.setCheckable(True)
        self.addAction(action)
        return action

    def groups_plot(self):
        if self.groups_dock.isVisible():
            self.groups_dock.hide()
        else:
            self.groups_dock.show_and_register()

    def update_all(self):
        self.groups_dock.update_all()
