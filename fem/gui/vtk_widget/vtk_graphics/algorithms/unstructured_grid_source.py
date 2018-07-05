from __future__ import print_function, absolute_import

import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase


class UnstructuredGridSource(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=0,
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self._input_data = vtk.vtkUnstructuredGrid()
        self._opt = None

    def set_input_data(self, data):
        assert isinstance(data, vtk.vtkUnstructuredGrid)
        self._input_data = data
        self.Modified()

    def RequestData(self, request, inInfo, outInfo):
        self._opt = vtk.vtkUnstructuredGrid.GetData(outInfo)
        self._opt.ShallowCopy(self._input_data)
        return 1
