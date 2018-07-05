from __future__ import print_function, absolute_import

import numpy as np
import vtk

from fem.gui.vtk_widget.vtk_graphics.algorithms.vtkmyCellPicker import vtkmyCellPicker
from fem.utilities.debug import show_stack_trace


class CellPicker(object):
    def __init__(self):
        self.Tolerance = 0.005
        self.ClosestCellId = -1
        self.ClosestCellGlobalId = -1

        self.selection_point = [0, 0, 0]
        self.p1World = [0, 0, 0]
        self.p2World = [0, 0, 0]

        self.cell_picker = vtkmyCellPicker()

        self.tolerances = np.zeros(10, dtype=np.float64)

        self.tolerances[:] = 0.005
        self.tolerances[0] = 0.3
        self.tolerances[1] = 0.3  # nodes
        self.tolerances[2] = 0.29  # lines
        self.tolerances[3] = 0.29  # ?
        self.tolerances[4] = 0.01  # rbes?

        self.tolerances_p = np.ctypeslib.as_ctypes(self.tolerances)

        self.PickPosition = np.zeros(3, dtype=np.float64)
        self.CellCenter = np.zeros(3, dtype=np.float64)
        self.cell_center_p = np.ctypeslib.as_ctypes(self.CellCenter)

    def toggle_visible(self):
        self.cell_picker.toggle_visible()

    def SetDataSet(self, data):
        pass

    def SetInputConnection(self, connection):
        self.cell_picker.SetInputConnection(connection)

    def SetActiveData(self, the_set, arr_name):
        self.cell_picker.set_active_data(the_set, arr_name)

    def SetTolerance(self, value):
        self.Tolerance = value

    def Pick(self, selectionX, selectionY, selectionZ, renderer):

        picked_id = self.cell_picker.pick_cell(selectionX, selectionY, selectionZ, renderer, self.tolerances_p)

        self.ClosestCellId = -1
        self.ClosestCellGlobalId = -1

        if picked_id < 0:
            return

        picking_data = self.cell_picker.GetInput()

        self.ClosestCellId = picking_data.GetCellData().GetArray("original_ids").GetValue(picked_id)
        self.ClosestCellGlobalId = picking_data.GetCellData().GetArray("global_ids").GetValue(picked_id)
        self.cell_picker.get_pick_position(self.cell_center_p)

    def GetClosestCellId(self):
        return self.ClosestCellId

    def GetClosestCellGlobalId(self):
        return self.ClosestCellGlobalId

    def finalize(self):
        # self.cell_picker.SetInputConnection(0)
        pass
