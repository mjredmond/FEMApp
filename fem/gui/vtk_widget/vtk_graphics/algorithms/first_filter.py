from __future__ import print_function, absolute_import

import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

from fem.model.bdf.card_info_list import CardInfoList
from .vtkmyFirstFilter import vtkmyFirstFilter

card_info = CardInfoList.instance()


class FirstFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self.first_filter = vtkmyFirstFilter()

        self.bdf_data = None
        """:type: mrNastran.bdf.bdf_data.BdfData"""

    def SetInputConnection(self, connection):
        VTKPythonAlgorithmBase.SetInputConnection(self, connection)
        self.first_filter.SetInputConnection(connection)

    def set_size(self, new_size):
        if new_size < 1:
            new_size = 1

        self.first_filter.set_coord_size(new_size)
        self.Modified()

    def set_bdf_data(self, bdf_data):
        self.bdf_data = bdf_data
        self.first_filter.set_coord_category(card_info.categories('COORD'))
        self.Modified()

    @property
    def size(self):
        return self.first_filter.get_coord_size()

    def RequestData(self, request, inInfo, outInfo):
        self.first_filter.Update()
        opt = vtk.vtkUnstructuredGrid.GetData(outInfo.GetInformationObject(0))
        opt.ShallowCopy(self.first_filter.GetOutputDataObject(0))

        return 1

    def finalize(self):
        self.first_filter.RemoveAllInputConnections(0)
        self.first_filter = None
        self.bdf_data = None
