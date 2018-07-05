from __future__ import print_function, absolute_import

import numpy as np
import vtk
from typing import List, Set
from vtk.util import numpy_support
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from fem.model.bdf.card_info_list import CardInfoList

card_info = CardInfoList.instance()


class vtkmyFirstFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self.coord_size = 5.
        self.coord_category = card_info.categories('COORD')

    def RequestData(self, request, inInfo, outInfo):
        input = vtk.vtkUnstructuredGrid.GetData(inInfo[0])
        output = vtk.vtkUnstructuredGrid.GetData(outInfo.GetInformationObject(0))

        output.ShallowCopy(input)

        if input.GetNumberOfCells() == 1:
            return 1

        points = output.GetPoints()

        if points is None:
            return 1

        cell_colors = vtk.vtkIntArray()
        cell_colors.SetName('colors')
        cell_colors.SetNumberOfTuples(output.GetNumberOfCells())

        output.GetCellData().AddArray(cell_colors)

        p0 = np.array([0., 0., 0.])
        p1 = np.array([0., 0., 0.])
        p3 = np.array([0., 0., 0.])
        p5 = np.array([0., 0., 0.])

        pts = vtk.vtkIdList()

        card_categories = output.GetCellData().GetArray('card_categories')

        # print(31)
        get_point = points.GetPoint
        # print(32)
        set_point = points.SetPoint
        # print(33)
        get_cell_points = output.GetCellPoints

        # print(4)

        set_cell_color = cell_colors.SetValue
        get_card_category = card_categories.GetValue

        # card_ids = output.GetCellData().GetAbstractArray('card_ids')
        # get_card_id = card_ids.GetValue

        # print(5)

        for i in range(output.GetNumberOfCells()):
            set_cell_color(i, 0)

            # print(get_card_id(i), self.coord_category, get_card_category(i))

            if get_card_category(i) == self.coord_category:
                get_cell_points(i, pts)

                p = get_point(pts.GetId(0))
                p0[:] = p

                p = get_point(pts.GetId(1))
                p1[:] = p

                p = get_point(pts.GetId(3))
                p3[:] = p

                p = get_point(pts.GetId(5))
                p5[:] = p

                p1 -= p0
                p3 -= p0
                p5 -= p0

                p1 /= np.linalg.norm(p1)
                p3 /= np.linalg.norm(p3)
                p5 /= np.linalg.norm(p5)

                p1 *= self.coord_size
                p3 *= self.coord_size
                p5 *= self.coord_size

                # print(51)
                set_point(pts.GetId(1), p1)
                set_point(pts.GetId(3), p3)
                set_point(pts.GetId(5), p5)
                # print(52)

        # print(6)

        return 1

    def set_coord_size(self, coord_size):
        self.coord_size = max(0.1, coord_size)
        self.Modified()

    def set_coord_category(self, category):
        self.coord_category = category
        self.Modified()

    def get_coord_size(self):
        return self.coord_size
