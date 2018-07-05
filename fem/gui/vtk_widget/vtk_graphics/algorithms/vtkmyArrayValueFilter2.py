from __future__ import print_function, absolute_import

import numpy as np
import vtk
from typing import List, Set
from vtk.util import numpy_support
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase


class vtkmyArrayValueFilter2(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self.selection_set = set()  # type: Set[int]
        self.selection_list = vtk.vtkIntArray()
        self.selection_node = vtk.vtkSelectionNode()
        self.selection = vtk.vtkSelection()
        self.ex = vtk.vtkExtractSelection()

        self.selection_list.SetName('global_ids')
        self.selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)
        self.selection_node.SetSelectionList(self.selection_list)
        self.selection.AddNode(self.selection_node)
        self.ex.ReleaseDataFlagOn()
        self.ex.SetInputDataObject(1, self.selection)

    def RequestData(self, request, inInfo, outInfo):
        # print('vtkmyArrayValueFilter2.RequestData')
        inp = vtk.vtkUnstructuredGrid.GetData(inInfo[0])
        opt = vtk.vtkUnstructuredGrid.GetData(outInfo.GetInformationObject(0))

        if not inp or inp.GetNumberOfCells() == 0:
            opt.ShallowCopy(opt)
            return 1

        # print(1)
        self.pre_filter(inp)
        # print(2)

        # print(3)
        self.ex.SetInputData(0, inp)
        # print(4)
        self.ex.Modified()
        # print(5)
        self.ex.Update()
        # print(6)

        new_opt = self.ex.GetOutputDataObject(0)

        opt.DeepCopy(new_opt)  # was doing a ShallCopy a while back, but it crashes now for some reason

        # print('vtkmyArrayValueFilter2.RequestData done!')

        return 1

    def set_array_name(self, name):
        self.selection_list.SetName(name)
        self.Modified()

    def set_selection(self, selection):
        self.selection_set = selection
        self.Modified()

    def reset(self):
        self.selection_list.Reset()
        self.Modified()

    def pre_filter(self, ugrid):
        self.selection_list.Reset()
        cell_data = ugrid.GetCellData()
        arr_name = self.selection_list.GetName()
        arr = cell_data.GetArray(arr_name)
        arr = numpy_support.vtk_to_numpy(arr)

        selection = self.selection_set
        insert_next_value = self.selection_list.InsertNextValue

        for i in range(arr.size):
            if arr[i] in selection:
                insert_next_value(i)


############################################


def _pre_filter_numba(arr, selection):
    result = []

    for i in range(arr.size):
        if arr[i] in selection:
            result.append(i)

    return result


try:
    import numba
    _pre_filter_numba = numba.jit(_pre_filter_numba)
except ImportError:
    pass


def pre_filter(self, ugrid):
    self.selection_list.Reset()
    cell_data = ugrid.GetCellData()
    arr_name = self.selection_list.GetName()
    arr = cell_data.GetArray(arr_name)
    arr = numpy_support.vtk_to_numpy(arr)

    print(1)
    result = _pre_filter_numba(arr, self.selection_set)
    print(2)

    insert_next_value = self.selection_list.InsertNextValue

    for i in range(len(result)):
        insert_next_value(result[i])


# vtkmyArrayValueFilter2.pre_filter = pre_filter
