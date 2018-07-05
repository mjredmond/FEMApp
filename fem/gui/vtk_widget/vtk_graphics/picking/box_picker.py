from __future__ import print_function, absolute_import

import vtk
from six.moves import range

from fem.utilities import MrSignal
from ...utilities.misc import create_box_frustum
from ...vtk_graphics import VTKGraphics
from ...vtk_graphics.rendering import vtkCameraManipulator


class BoxPicker(vtkCameraManipulator):
    def __init__(self):
        vtkCameraManipulator.__init__(self)

        self.picked_data = None
        self.box_picker = vtk.vtkExtractSelectedFrustum()
        self._start_position = [0, 0]
        self._end_position = [0, 0]
        self._pixel_array = vtk.vtkUnsignedCharArray()

        self.ex = vtk.vtkExtractSelection()
        self.selection_node = vtk.vtkSelectionNode()
        self.selection_node.SetContentType(vtk.vtkSelectionNode.THRESHOLDS)
        self.ex_selection = vtk.vtkSelection()
        self.ex_selection.AddNode(self.selection_node)

        self.ex.SetInputConnection(0, self.box_picker.GetOutputPort())
        self.ex.SetInputData(1, self.ex_selection)

        self._down_pos = None
        self._up_pos = None

        self.iren = None
        self.ren_win = None
        self.ren_win_size = None

        self.data_picked = MrSignal()
        self.done_picking = MrSignal()

        self._picking_active = False

        # self.vtk_graphics = VTKGraphics.instance()

        from .picking_manager import PickingManager
        self.picking_manager = PickingManager.instance()

    def set_input_connection(self, port):
        self.box_picker.SetInputConnection(port)

    def begin_picking(self, interactor):
        self.iren = interactor

        self.ren_win = interactor.GetRenderWindow()
        self.ren_win_size = self.ren_win.GetSize()

        self._start_position[0] = interactor.GetEventPosition()[0]
        self._start_position[1] = interactor.GetEventPosition()[1]
        self._end_position[0] = self._start_position[0]
        self._end_position[1] = self._start_position[1]

        self._pixel_array.Reset()
        self._pixel_array.SetNumberOfComponents(4)
        self._pixel_array.SetNumberOfTuples(self.ren_win_size[0] * self.ren_win_size[1])

        self.ren_win.GetRGBACharPixelData(0, 0, self.ren_win_size[0] - 1, self.ren_win_size[1] - 1, 1,
                                          self._pixel_array)

        pos = interactor.GetEventPosition()

        self._down_pos = pos

        self._picking_active = True

    def end_picking(self, renderer, interactor):

        pos = interactor.GetEventPosition()

        self._up_pos = pos

        self._frustum = create_box_frustum(self._down_pos[0], self._down_pos[1],
                                           self._up_pos[0], self._up_pos[1], renderer)

        self.box_picker.SetFrustum(self._frustum)

        self.something_picked()

        self._picking_active = False
        self.done_picking.emit()

    def get_picking_frustums(self):
        return [self._frustum]

    def something_picked(self):
        self.box_picker.Modified()
        self.box_picker.Update()

        global_ids = self.box_picker.GetOutput().GetCellData().GetArray("global_ids")

        if global_ids is None:
            self.picking_manager.set_picked_data([])
            return

        get_value = global_ids.GetValue

        data = []

        for i in range(global_ids.GetNumberOfTuples()):
            data.append(get_value(i))

        self.picking_manager.set_picked_data(data)

    def _redraw_picking_box(self, interactor):
        tmp_array = vtk.vtkUnsignedCharArray()
        tmp_array.DeepCopy(self._pixel_array)

        min = [0, 0]
        max = [0, 0]

        size = self.ren_win_size

        if self._start_position[0] <= self._end_position[0]:
            min[0] = self._start_position[0]
        else:
            min[0] = self._end_position[0]

        if min[0] < 0:
            min[0] = 0
        if min[0] >= size[0]:
            min[0] = size[0] - 1

        if self._start_position[1] <= self._end_position[1]:
            min[1] = self._start_position[1]
        else:
            min[1] = self._end_position[1]

        if min[1] < 0:
            min[1] = 0
        if min[1] >= size[1]:
            min[1] = size[1] - 1

        if self._end_position[0] > self._start_position[0]:
            max[0] = self._end_position[0]
        else:
            max[0] = self._start_position[0]

        if max[0] < 0:
            max[0] = 0
        if max[0] >= size[0]:
            max[0] = size[0] - 1

        if self._end_position[1] > self._start_position[1]:
            max[1] = self._end_position[1]
        else:
            max[1] = self._start_position[1]

        if max[1] < 0:
            max[1] = 0
        if max[1] >= size[1]:
            max[1] = size[1] - 1

        for i in range(min[0], max[0] + 1):
            index1 = min[1] * size[0] + i
            tmp_array.SetTuple4(index1, 255, 120, 0, 1)

            index1 = max[1] * size[0] + i
            tmp_array.SetTuple4(index1, 255, 120, 0, 1)

        for i in range(min[1] + 1, max[1]):
            index1 = i*size[0] + min[0]
            tmp_array.SetTuple4(index1, 255, 120, 0, 1)

            index1 = i*size[0] + max[0]
            tmp_array.SetTuple4(index1, 255, 120, 0, 1)

        interactor.GetRenderWindow().SetRGBACharPixelData(0, 0, size[0] - 1, size[1] - 1, tmp_array, 0)
        interactor.GetRenderWindow().Frame()

    def OnButtonDown(self, x, y, ren, iren):
        self.begin_picking(iren)

    def OnButtonUp(self, x, y, ren, iren):
        self.end_picking(ren, iren)

    def OnMouseMove(self, x, y, ren, iren):
        if not self._picking_active:
            return

        if not ren:
            return

        self._end_position[0] = iren.GetEventPosition()[0]
        self._end_position[1] = iren.GetEventPosition()[1]
        self.ren_win_size = self.ren_win.GetSize()

        size = self.ren_win_size

        if self._end_position[0] > size[0] - 1:
            self._end_position[0] = size[0] - 1

        if self._end_position[0] < 0:
            self._end_position[0] = 0

        if self._end_position[1] > size[1] - 1:
            self._end_position[1] = size[1] - 1

        if self._end_position[1] < 0:
            self._end_position[1] = 0

        self._redraw_picking_box(iren)

    def PrintSelf(self):
        super(self, BoxPicker).PrintSelf()
        print("Center: %f, %f, %f" % (self.Center[0], self.Center[1], self.Center[2]))

    def finalize(self):
        # self.vtk_graphics = None
        self.picking_manager = None
