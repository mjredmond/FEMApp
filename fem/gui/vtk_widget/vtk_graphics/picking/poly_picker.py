from __future__ import print_function, absolute_import

import vtk
from six.moves import range

from fem.utilities import MrSignal
from fem.gui.vtk_widget.vtk_graphics.rendering import vtkCameraManipulator
from ..algorithms.poly_pick_filter import PolyPickFilter
from ...utilities.misc import create_box_frustum, display_to_world, get_line_pixels
from ...vtk_graphics import VTKGraphics


class PolyPicker(vtkCameraManipulator):
    def __init__(self):
        vtkCameraManipulator.__init__(self)

        self._start_position = [0, 0]
        self._end_position = [0, 0]
        self._pixel_array = vtk.vtkUnsignedCharArray()

        self._left_button_down = False
        self._ctrl_left_button_down = False
        self._right_button_down = False
        self._middle_button_down = False

        self._down_pos = None
        self._up_pos = None

        self._point_list = []

        self.renderer = None
        self.iren = None

        #self.reset_polygon()
        self._points = 0

        self.polygon = vtk.vtkPolygon()

        self.poly_data = vtk.vtkPolyData()
        self.poly_points = vtk.vtkPoints()
        self.poly_data.SetPoints(self.poly_points)

        self.cell_array = vtk.vtkCellArray()
        self.cell_array.InsertNextCell(self.polygon)
        self.cell_array.Squeeze()

        self.poly_data.SetPolys(self.cell_array)

        self.done_picking = MrSignal()
        self._picking_active = False

        self.poly_pick_filter = PolyPickFilter()
        self.poly_pick_filter.set_poly_pick_data(self.poly_data)

        self.vtk_graphics = VTKGraphics.instance()

        from .picking_manager import PickingManager
        self.picking_manager = PickingManager.instance()

    def set_input_connection(self, port):
        self.poly_pick_filter.SetInputConnection(port)

    def reset_polygon(self):
        self._point_list = []
        self._points = 0
        self.poly_points.Reset()
        self.polygon.GetPointIds().Reset()

    def begin_picking(self, renderer, interactor):
        self.reset_polygon()

        self.renderer = renderer
        self.iren = interactor

        self.poly_pick_filter.set_renderer(renderer)

        self.ren_win = interactor.GetRenderWindow()
        self.ren_win_size = self.ren_win.GetSize()

        self._pixel_array.Reset()
        self._pixel_array.SetNumberOfComponents(4)
        self._pixel_array.SetNumberOfTuples(self.ren_win_size[0] * self.ren_win_size[1])

        self.ren_win.GetRGBACharPixelData(0, 0, self.ren_win_size[0] - 1, self.ren_win_size[1] - 1, 1,
                                          self._pixel_array)

        pos = interactor.GetEventPosition()

        self._first_point = pos
        self._last_point = pos

        self._points = 0

        self._picking_active = True

    def self_intersecting(self):

        def on_segment(p, r, q):

            max0 = max(p[0], r[0])
            min0 = min(p[0], r[0])

            max1 = max(p[1], r[1])
            min1 = min(p[1], r[1])

            if min0 <= q[0] <= max0 and min1 <= q[1] <= max1:
                return True
            else:
                return False

        def orientation(p, r, q):
            val = int((q[1] - p[1])*(r[0] - q[0]) - (q[0] - p[0])*(r[1] - q[1]))

            if val == 0:
                return 0

            if val > 0:
                return 1
            else:
                return 2

        def does_intersect(p1, q1, p2, q2):

            if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
                return False

            o1 = orientation(p1, q1, p2)
            o2 = orientation(p1, q1, q2)
            o3 = orientation(p2, q2, p1)
            o4 = orientation(p2, q2, q1)

            if o1 != o2 and o3 != o4:
                return True

            if o1 == 0 and on_segment(p1, q1, p2):
                return True

            if o2 == 0 and on_segment(p1, q1, q2):
                return True

            if o3 == 0 and on_segment(p2, q2, p1):
                return True

            if o4 == 0 and on_segment(p2, q2, q1):
                return True

            return False

        pl = self._point_list

        points = len(pl)

        if points <= 2:
            return False

        e1 = [pl[0], pl[points-1]]
        e2 = [pl[points-2], pl[points-1]]

        for i in range(1, points-1):
            p1 = pl[i]
            p2 = pl[i-1]

            if does_intersect(p1, p2, e1[0], e1[1]) or does_intersect(p1, p2, e2[0], e2[1]):
                return True

        return False

    def add_point(self, interactor, renderer):

        def distance(p1, p2):
            sum = (p1[0] - p2[0])**2
            sum += (p1[1] - p2[1])**2

            return sum ** 0.5

        pos = interactor.GetEventPosition()

        if self._points > 2 and (distance(pos, self._last_point) <= 5 or distance(pos, self._first_point) <= 5):
            self.end_picking(self.renderer, interactor)
            return True

        self._point_list.append(pos)

        if self.self_intersecting():
            self._point_list.pop()
            return False

        world_point = display_to_world(pos, renderer, .001)
        self.poly_points.InsertNextPoint(world_point[:3])

        self._last_point = pos

        self.polygon.GetPointIds().InsertNextId(self._points)
        self.polygon.Modified()

        self._points += 1

        return False

    def end_picking(self, renderer, interactor):
        self.something_picked()
        self._picking_active = False
        self.done_picking.emit()

    def get_picking_frustums(self):
        return []

    def something_picked(self):
        self.poly_points.Modified()
        self.polygon.Modified()
        self.poly_data.SetPoints(self.poly_points)
        self.cell_array.Reset()
        self.cell_array.InsertNextCell(self.polygon)
        self.cell_array.Squeeze()
        self.poly_data.SetPolys(self.cell_array)
        self.poly_data.Modified()

        self.poly_pick_filter.set_poly_pick_data(self.poly_data)
        self.poly_pick_filter.Modified()
        self.poly_pick_filter.Update()

        global_ids = self.poly_pick_filter.GetOutputDataObject(0).GetCellData().GetArray("global_ids")

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

        point_list = self._point_list[:]
        point_list.append(self._end_position)

        my_int = int

        for i in range(1, len(point_list)):
            p1 = point_list[i-1]
            p2 = point_list[i]

            points = get_line_pixels(p1, p2)

            for p in points:
                index1 = p[1] * size[0] + p[0]
                tmp_array.SetTuple4(index1, 255, 120, 0, 1)

        p1 = list(point_list[0])
        p2 = list(point_list[-1])

        points = get_line_pixels(p1, p2)
        for p in points:
            index1 = p[1] * size[0] + p[0]
            tmp_array.SetTuple4(index1, 255, 120, 0, 1)

        p1[1] += 1
        p2[1] += 1

        points = get_line_pixels(p1, p2)
        for p in points:
            index1 = p[1] * size[0] + p[0]
            tmp_array.SetTuple4(index1, 255, 120, 0, 1)

        p1[1] -= 2
        p2[1] -= 2

        points = get_line_pixels(p1, p2)
        for p in points:
            index1 = p[1] * size[0] + p[0]
            tmp_array.SetTuple4(index1, 255, 120, 0, 1)

        p1[1] += 1

        point_list = [[p1[0] - 5, p1[1] + 5], [p1[0] + 5, p1[1] + 5], [p1[0] + 5, p1[1] - 5], [p1[0] - 5, p1[1] - 5]]
        point_list.append(point_list[0])

        for i in range(1, len(point_list)):
            p1 = point_list[i-1]
            p2 = point_list[i]

            points = get_line_pixels(p1, p2)

            for p in points:
                index1 = p[1] * size[0] + p[0]
                tmp_array.SetTuple4(index1, 255, 120, 0, 1)

        interactor.GetRenderWindow().SetRGBACharPixelData(0, 0, size[0] - 1, size[1] - 1, tmp_array, 0)
        interactor.GetRenderWindow().Frame()

    def OnButtonDown(self, x, y, ren, iren):
        if self._picking_active:
            self.add_point(iren, ren)
        else:
            self.begin_picking(ren, iren)
            self.add_point(iren, ren)

    def OnButtonUp(self, x, y, ren, iren):
        #self.end_picking(ren, iren)
        pass

    def OnMouseMove(self, x, y, ren, iren):
        if not self._picking_active:
            return

        if not ren:
            return

        self.renderer = ren
        self.iren = iren

        pos = iren.GetEventPosition()

        self._end_position[0] = pos[0]
        self._end_position[1] = pos[1]
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
        super(self, PolyPicker).PrintSelf()
        print("Center: %f, %f, %f" % (self.Center[0], self.Center[1], self.Center[2]))

    def finalize(self):
        self.vtk_graphics = None
        self.picking_manager = None
