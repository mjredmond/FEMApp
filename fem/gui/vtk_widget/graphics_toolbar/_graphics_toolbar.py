from __future__ import print_function, absolute_import

from qtpy import QtGui, QtCore, QtWidgets

from ..gui_helper import GUIPath
from ..vtk_graphics import VTKGraphics
from ..vtk_graphics.picking import PickingManager
from ..vtk_graphics.picking import SinglePicker

picking_manager = PickingManager.instance()

vtk_graphics = VTKGraphics.instance()

gui_path = GUIPath("graphics_toolbar/images")


class RotationCenterPicker(SinglePicker):
    def pick(self, screen_pos, cell_pos, picked_global_id):
        self.vtk_graphics.set_rotation_center(cell_pos)
        self.done.emit()


class GraphicsToolbar(QtWidgets.QToolBar):
    def __init__(self, parent):
        super(GraphicsToolbar, self).__init__(parent)

        self.fit_view_action = self._add_action(
            QtGui.QIcon(
                gui_path("fit_view.png")
            ),
            "&Fit View",
            self,
            statusTip="Fit view",
            triggered=self.fit_view
        )

        self.rotation_center_action = self._add_action(
            QtGui.QIcon(
                gui_path("rotation_center.png")
            ),
            "&Set Rotation Center",
            self,
            statusTip="Set rotation center",
            triggered=self.rotation_center
        )

        self.rotation_center_action.setCheckable(True)

        self.zoom_out_action = self._add_action(
            QtGui.QIcon(
                gui_path("zoom_out.png")
            ),
            "&Zoom out",
            self,
            statusTip="Zoom out",
            triggered=self.zoom_out
        )

        self.zoom_in_action = self._add_action(
            QtGui.QIcon(
                gui_path("zoom_in.png")
            ),
            "&Zoom in",
            self,
            statusTip="Zoom in",
            triggered=self.zoom_in
        )

        self.rotation_center_picker = RotationCenterPicker()
        self.rotation_center_picker.done.connect(self._picking_done)

        self._pass = False

        self.setIconSize(QtCore.QSize(16, 16))

    def _picking_done(self, *args):
        self.rotation_center_action.setChecked(False)
        picking_manager.unload_single_picker(self.rotation_center_picker)

    def _add_action(self, *args, **kwargs):
        action = QtWidgets.QAction(*args, **kwargs)
        self.addAction(action)
        return action

    def fit_view(self):
        vtk_graphics.fit_view()

    def rotation_center(self):
        picking_manager.register_single_picker(self.rotation_center_picker)

    def zoom_out(self):
        pass

    def zoom_in(self):
        pass
