from __future__ import print_function, absolute_import

import numpy as np
import vtk
from typing import List, Set
from vtk.util import numpy_support
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from fem.model.bdf.card_info_list import CardInfoList

card_info = CardInfoList.instance()


class vtkmyCellPickerFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=0)

        self.cc = vtk.vtkCellCenters()

        # tried using a vtkCellLocator for FindCellsAlongLine
        # but it wouldn't find the vertex cells for some reason...
        self.tree = vtk.vtkKdTree()

        self._empty_dataset = False

    def SetInputConnection(self, connection):
        VTKPythonAlgorithmBase.SetInputConnection(self, connection)
        self.cc.SetInputConnection(connection)

    def RequestData(self, request, inInfo, outInfo):
        inp = vtk.vtkUnstructuredGrid.GetData(inInfo[0])
        if not inp or inp.GetNumberOfCells() == 0:
            self._empty_dataset = True
            return 1
        self.cc.Update()
        self.tree.BuildLocatorFromPoints(self.cc.GetOutput().GetPoints())
        self._empty_dataset = False
        return 1

    def FindCellsAlongLine(self, p1, p2, ids):
        if self._empty_dataset:
            return
        p1 = np.array(p1)
        p2 = np.array(p2)
        delta = p2 - p1
        dist = np.linalg.norm(delta)
        r = dist / 50.
        divisions = int(dist / r) + 1
        r = dist / divisions

        delta /= dist

        FindPointsWithinRadius = self.tree.FindPointsWithinRadius

        _ids = vtk.vtkIdList()

        _id_set = set()

        _d = 0.
        while True:
            p = p1 + delta * _d
            FindPointsWithinRadius(r, p[:3], _ids)

            for i in range(_ids.GetNumberOfIds()):
                _id_set.add(_ids.GetId(i))

            _d += 0.5 * r

            if _d > dist:
                break

        ids.Reset()

        for i in sorted(_id_set):
            ids.InsertNextId(i)
