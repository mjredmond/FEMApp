from __future__ import print_function, absolute_import

import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from fem.gui.vtk_widget.vtk_graphics.algorithms.vtkmyVisibleFilter2 import vtkmyVisibleFilter2
from ...algorithms import FirstFilter


# from vtk_fem.selection_data import selection_data


class VisibleFilter_new(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self.visible_filter = vtkmyVisibleFilter2()
        self.coord_filter = FirstFilter()
        self.coord_filter.SetInputConnection(self.visible_filter.GetOutputPort(0))

    def set_bdf_data(self, bdf_data):
        self.coord_filter.set_bdf_data(bdf_data)
        self.Modified()

    def set_visible_ids(self, ids):
        self.visible_filter.set_visible_ids(ids)

    def set_active_groups(self, groups):
        self.visible_filter.set_active_groups(groups)

    def set_active_types(self, types):
        self.visible_filter.set_active_types(types)

    def toggle_visible(self):
        self.visible_filter.toggle_visible()

    def SetInputConnection(self, connection):
        VTKPythonAlgorithmBase.SetInputConnection(self, connection)
        self.visible_filter.SetInputConnection(connection)

    def RequestData(self, request, inInfo, outInfo):
        self.visible_filter.Modified()
        self.coord_filter.Update()

        opt = vtk.vtkUnstructuredGrid.GetData(outInfo.GetInformationObject(0))
        opt.ShallowCopy(self.coord_filter.GetOutputDataObject(0))

        return 1


class VisibleFilter(vtkmyVisibleFilter2):
    def __init__(self):
        vtkmyVisibleFilter2.__init__(self)
