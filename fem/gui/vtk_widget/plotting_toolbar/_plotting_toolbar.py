from __future__ import print_function, absolute_import

from qtpy import QtGui, QtCore, QtWidgets

from ._plotting_dock import PlottingDock
from ..gui_helper import GUIPath
from ..vtk_graphics import VTKGraphics

gui_path = GUIPath("plotting_toolbar/images")
vtk_graphics = VTKGraphics.instance()


class PlottingToolbar(QtWidgets.QToolBar):
    def __init__(self, main_window):
        super(PlottingToolbar, self).__init__(main_window)

        self.plot_erase_action = self._add_action(QtGui.QIcon(gui_path("plot_erase.png")),
                                                    "&Plot or Erase", self,
                                                    statusTip="Plot or erase elements",
                                                    triggered=self.plot_erase)

        self.swap_visible_action = self._add_action(QtGui.QIcon(gui_path("swap_visible.png")),
                                                    "&Swap Visible Space", self,
                                                    statusTip="Swap visible space",
                                                    triggered=self.swap_visible)
        self.swap_visible_action.setCheckable(True)

        self.swap_perspective_action = self._add_action(QtGui.QIcon(gui_path("parallel_projection.png")),
                                                    "&Swap Perspective", self,
                                                    statusTip="Swap perspective",
                                                    triggered=self.swap_perspective)
        self._perspective = False

        self._pass = False

        self.setIconSize(QtCore.QSize(16, 16))

        self.plotting_dock = PlottingDock(main_window)

        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.plotting_dock)

        self.plotting_dock.hide()

    def _add_action(self, *args, **kwargs):
        action = QtWidgets.QAction(*args, **kwargs)
        #action.setCheckable(True)
        self.addAction(action)
        return action

    def plot_erase(self):
        if self.plotting_dock.isVisible():
            self.plotting_dock.hide()
        else:
            self.plotting_dock.show_and_register()

    def swap_visible(self):
        vtk_graphics.swap_visible()

    def swap_perspective(self):
        if self._perspective:
            self.swap_perspective_action.setIcon(QtGui.QIcon(gui_path("parallel_projection.png")))
        else:
            self.swap_perspective_action.setIcon(QtGui.QIcon(gui_path("perspective_projection.png")))

        self._perspective = not self._perspective

        vtk_graphics.switch_perspective()
