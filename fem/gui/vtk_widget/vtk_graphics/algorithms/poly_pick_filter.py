from __future__ import print_function, absolute_import

import vtk
from six.moves import range
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from ...utilities.misc import (create_triangle_frustum)


class PolyPickFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self.append_filter = vtk.vtkAppendFilter()
        self.append_filter.ReleaseDataFlagOn()
        self.triangle_filter = vtk.vtkTriangleFilter()
        self.planes = vtk.vtkPlanes()

        self.ex = vtk.vtkExtractSelectedFrustum()
        self.ex.ReleaseDataFlagOn()

        self.poly_pick_data = None
        self.renderer = None

    def set_poly_pick_data(self, data):
        self.poly_pick_data = data
        self.triangle_filter.SetInputData(self.poly_pick_data)
        self.triangle_filter.Modified()
        self.Modified()

    def set_renderer(self, renderer):
        self.renderer = renderer

    def RequestData(self, request, inInfo, outInfo):

        if self.renderer is None or self.poly_pick_data is None:
            return 1

        inp = vtk.vtkUnstructuredGrid.GetData(inInfo[0])

        if inp is None or inp.GetNumberOfCells() == 0:
            return 1

        opt = vtk.vtkUnstructuredGrid.GetData(outInfo.GetInformationObject(0))

        self.triangle_filter.Modified()
        self.triangle_filter.Update()

        triangles = self.triangle_filter.GetOutput()

        if triangles.GetNumberOfCells() == 0:
            return 1

        self.append_filter.RemoveAllInputs()

        self.ex.SetInputData(inp)

        for i in range(triangles.GetNumberOfCells()):

            tri = triangles.GetCell(i)

            ids = tri.GetPointIds()

            p1 = triangles.GetPoint(ids.GetId(0))
            p2 = triangles.GetPoint(ids.GetId(1))
            p3 = triangles.GetPoint(ids.GetId(2))

            frustum = create_triangle_frustum(p1, p2, p3, self.renderer)

            self.ex.SetFrustum(frustum)
            self.ex.Modified()
            self.ex.Update()

            out = vtk.vtkUnstructuredGrid()
            out.ShallowCopy(self.ex.GetOutput())

            self.append_filter.AddInputData(out)

        self.append_filter.Modified()
        self.append_filter.Update()

        opt.ShallowCopy(self.append_filter.GetOutput())

        return 1
