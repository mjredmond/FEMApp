from __future__ import print_function, absolute_import

import vtk
from typing import List, Set
from vtk import mutable
from vtk.util import numpy_support
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from .vtkmyCellPickerFilter import vtkmyCellPickerFilter


class vtkmyPickingRay(object):
    def __init__(self):
        self.selection_point = [0., 0., 0.]  # List[float]
        self.pick_position = [0., 0., 0.]  # List[float]
        self.p1_world = [0., 0., 0., 0.]  # List[float]
        self.p2_world = [0., 0., 0., 0.]  # List[float]


class vtkmyCellPicker(object):
    def __init__(self):
        self.my_picking_ray = vtkmyPickingRay()
        self.visible_only = False
        self.active_set = set()
        self.active_array = vtk.vtkIntArray()
        self.array_name = ''

        self.filter = vtkmyCellPickerFilter()

    def SetInputConnection(self, connection):
        self.filter.SetInputConnection(connection)

    def GetInput(self):
        return self.filter.cc.GetInput()

    def picking_ray(self, x, y, z, renderer, results):
        del results.selection_point[:]
        results.selection_point.extend([x, y, z])
        camera = renderer.GetActiveCamera()

        _pos = camera.GetPosition()
        cameraPos = [_pos[0], _pos[1], _pos[2], 1.]

        _pos = camera.GetFocalPoint()
        cameraFP = [_pos[0], _pos[1], _pos[2], 1.]

        renderer.SetWorldPoint(cameraFP[0], cameraFP[1], cameraFP[2], cameraFP[3])
        renderer.WorldToDisplay()

        _pos = renderer.GetDisplayPoint()

        z = _pos[2]
        renderer.SetDisplayPoint(x, y, z)
        renderer.DisplayToWorld()

        _pos = renderer.GetWorldPoint()

        if _pos[3] == 0.:
            print('Bad homogeneous coordinates!')
            return 0

        worldCoords = _pos

        PickPosition = results.pick_position
        PickPosition[0] = worldCoords[0] / worldCoords[3]
        PickPosition[1] = worldCoords[1] / worldCoords[3]
        PickPosition[2] = worldCoords[2] / worldCoords[3]

        ray = [0., 0., 0.]
        cameraDOP = [0., 0., 0.]
        magnitude = 0.

        for i in range(3):
            ray[i] = PickPosition[i] - cameraPos[i]
            cameraDOP[i] = cameraFP[i] - cameraPos[i]
            magnitude += cameraDOP[i] ** 2

        magnitude = magnitude ** 0.5

        cameraDOP[0] /= magnitude
        cameraDOP[1] /= magnitude
        cameraDOP[2] /= magnitude

        dot_product = cameraDOP[0] * ray[0] + cameraDOP[1] * ray[1] + cameraDOP[2] * ray[2]

        if dot_product == 0.:
            print('Cannot process points!')
            return 0

        rayLength = dot_product

        clipRange = camera.GetClippingRange()

        p1World = results.p1_world
        p2World = results.p2_world

        if camera.GetParallelProjection():
            tF = clipRange[0] - rayLength
            tB = clipRange[1] - rayLength

            for i in range(3):
                p1World[i] = PickPosition[i] + tF * cameraDOP[i]
                p2World[i] = PickPosition[i] + tB * cameraDOP[i]

        else:
            tF = clipRange[0] / rayLength
            tB = clipRange[1] / rayLength

            for i in range(3):
                p1World[i] = cameraPos[i] + tF * ray[i]
                p2World[i] = cameraPos[i] + tB * ray[i]

        p1World[3] = p2World[3] = 1.

        return 1.

    def pick_cell(self, x, y, z, renderer, tols):
        if self.visible_only:
            return self.pick_cell_visible(x, y, z, renderer, tols)
        else:
            return self.pick_cell_any(x, y, z, renderer, tols)

    def set_active_data(self, data, name):
        self.active_set = data
        self.array_name = name

    def get_pick_position(self, pick_position):
        pick_position[0] = self.my_picking_ray.pick_position[0]
        pick_position[1] = self.my_picking_ray.pick_position[1]
        pick_position[2] = self.my_picking_ray.pick_position[2]

    def toggle_visible(self):
        self.visible_only = not self.visible_only

    def pick_cell_visible(self, x, y, z, renderer, tols):
        if not self.picking_ray(x, y, z, renderer, self.my_picking_ray):
            print('Picking ray failed!')
            return -1

        self.filter.cc.Update()
        picking_data = self.filter.cc.GetInput()

        raw_arr = None

        if picking_data:
            if picking_data.GetCellData().HasArray(self.array_name):
                raw_arr = numpy_support.vtk_to_numpy(picking_data.GetCellData().GetArray(self.array_name))

        if raw_arr is None:
            return -1

        p1World = self.my_picking_ray.p1_world
        p2World = self.my_picking_ray.p2_world

        _p1world = p1World[:3]
        _p2world = p2World[:3]

        t = mutable(0.)
        x_ = [0., 0., 0.]
        pcoords = [0., 0., 0.]
        subId = mutable(0)

        min_i = -1
        min_d = 999999999.

        # line = vtk.vtkLine()

        # d = 0.
        min_x = [0., 0., 0.]

        ids = vtk.vtkIdList()

        self.filter.FindCellsAlongLine(_p1world, _p2world, ids)

        for i in range(ids.GetNumberOfIds()):
            id = ids.GetId(i)
            cell = picking_data.GetCell(id)
            cell_type = cell.GetCellType()

            if cell.IntersectWithLine(_p1world, _p2world, tols[cell_type], t, x_, pcoords, subId):
                d = float(t)

                if d < min_d:
                    if raw_arr is not None and self.active_set and raw_arr[id] in self.active_set:
                        min_i = id
                    else:
                        min_i = -1

                    min_d = d
                    min_x[0] = x_[0]
                    min_x[1] = x_[1]
                    min_x[2] = x_[2]

        if min_i >= 0:
            self.my_picking_ray.pick_position[0] = min_x[0]
            self.my_picking_ray.pick_position[1] = min_x[1]
            self.my_picking_ray.pick_position[2] = min_x[2]

        return min_i

    def pick_cell_any(self, x, y, z, renderer, tols):
        if not self.picking_ray(x, y, z, renderer, self.my_picking_ray):
            print('Picking ray failed!')
            return -1

        # self.filter.Modified()
        self.filter.Update()
        cc_data = self.filter.cc.GetOutput()
        picking_data = self.filter.cc.GetInput()

        raw_arr = None

        if picking_data:
            if picking_data.GetCellData().HasArray(self.array_name):
                raw_arr = numpy_support.vtk_to_numpy(picking_data.GetCellData().GetArray(self.array_name))
        else:
            return -1

        p1World = self.my_picking_ray.p1_world
        p2World = self.my_picking_ray.p2_world

        _p1world = p1World[:3]
        _p2world = p2World[:3]

        t = mutable(0.)
        x_ = [0., 0., 0.]
        pcoords = [0., 0., 0.]
        subId = mutable(0)

        min_i = [-1]
        min_d = 999999999.

        line = vtk.vtkLine()
        distance_to_line = line.DistanceToLine

        cc_get_point = cc_data.GetPoint

        # d = 0.
        min_x = [0., 0., 0.]

        active_set = self.active_set

        ids = vtk.vtkIdList()

        # self._cell_locator.Update()
        # self._cell_locator.cell_locator.FindCellsAlongLine(_p1world, _p2world, 1., ids)

        self.filter.FindCellsAlongLine(_p1world, _p2world, ids)

        # original_ids = self._cell_locator.cell_locator.GetDataSet().GetCellData().GetArray('original_ids')

        # _cell_type = -1

        for i in range(ids.GetNumberOfIds()):
            id = ids.GetId(i)
            # id = i
            cell = picking_data.GetCell(id)

            # cell = picking_data.GetCell(i)
            cell_type = cell.GetCellType()

            # if cell_type == 1:
            #     print(cell_type)

            if cell.IntersectWithLine(_p1world, _p2world, tols[cell_type], t, x_, pcoords, subId):
                d = distance_to_line(cc_get_point(id), _p1world, _p2world)

                try:
                    if d < min_d and raw_arr[id] in active_set:
                        min_d = d
                        min_i[0] = id
                        min_x[0] = x_[0]
                        min_x[1] = x_[1]
                        min_x[2] = x_[2]
                        # _cell_type = cell_type
                except Exception:
                    pass

        if min_i[0] >= 0:
            self.my_picking_ray.pick_position[0] = min_x[0]
            self.my_picking_ray.pick_position[1] = min_x[1]
            self.my_picking_ray.pick_position[2] = min_x[2]
            # print('cell type = ', _cell_type)

        return min_i[0]
