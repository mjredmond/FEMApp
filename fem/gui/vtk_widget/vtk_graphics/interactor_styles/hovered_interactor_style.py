from __future__ import print_function, absolute_import

import vtk

from fem.utilities import MrSignal
from ..pipelines.hovered import CellPicker
from ...vtk_graphics import VTKGraphics
from ...vtk_graphics.rendering import vtkCameraManipulator


class HoveredInteractorStyle(vtkCameraManipulator):
    def __init__(self):
        vtkCameraManipulator.__init__(self)

        self.cell_picker = CellPicker()

        self.hovered_data = None
        self.visible_filter = None
        self.pickable_types = None

        self.picked_id = -1

        self.vtk_graphics = VTKGraphics.instance()

        self.key_down = MrSignal()

    def visible_only(self):
        self.cell_picker.toggle_visible()

    def set_hovered_data(self, hovered_data):
        self.hovered_data = hovered_data

    def set_visible_filter(self, visible_filter):
        self.visible_filter = visible_filter
        self.cell_picker.SetInputConnection(self.visible_filter.GetOutputPort())

    def set_pickable_types(self, pickable_types):
        self.pickable_types = pickable_types
        self.cell_picker.SetActiveData(self.pickable_types.raw_pointer(), 'card_types')

    def OnMouseMove(self, x, y, ren, iren):
        self.cell_picker.Pick(x, y, 0, ren)

        picked_id = self.cell_picker.GetClosestCellGlobalId()

        if self.picked_id != picked_id:
            self.picked_id = picked_id
            if picked_id > 0:
                self.hovered_data.set_data(picked_id)
            else:
                self.hovered_data.set_data([])

            self.vtk_graphics.hovered_filter.Modified()
            self.vtk_graphics.render()

    def OnKeyDown(self, iren):
        super(HoveredInteractorStyle, self).OnKeyDown(iren)
        self.key_down.emit(self.KeyCode)

    def unload(self):
        self.hovered_data.set_data([])

    def finalize(self):
        self.cell_picker.finalize()
        self.cell_picker = None
        self.hovered_data = None
        self.visible_filter = None
        self.pickable_types = None

        self.vtk_graphics = None
