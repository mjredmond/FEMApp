from __future__ import print_function, absolute_import

from six.moves import range

from fem.utilities import MrSignal, debuginfo
from fem.gui.vtk_widget.vtk_graphics.algorithms.vtkmyArrayValueFilter2 import vtkmyArrayValueFilter2


class HoveredFilter(vtkmyArrayValueFilter2):
    def __init__(self):
        vtkmyArrayValueFilter2.__init__(self)

        #self.set_selection(selection.raw_pointer())

        #self.filter_modified = MrSignal()

        #selection_data.hovered.data_changed.connect(self._data_changed)

    #def _data_changed(self):
    #    self.set_selection(selection_data.hovered.raw_pointer())
    #    self.filter_modified.emit()

import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase

class HoveredFilter2(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self.selection_list = vtk.vtkIntArray()
        self.selection_list.SetName("global_ids")

        self.selection_node = vtk.vtkSelectionNode()
        self.selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)
        self.selection_node.SetSelectionList(self.selection_list)

        self.selection = vtk.vtkSelection()
        self.selection.AddNode(self.selection_node)

        self.ex = vtk.vtkExtractSelection()
        self.ex.SetInputDataObject(1, self.selection)
        #self.ex.ReleaseDataFlagOn()

        self.selection_set = None

    def SetInputConnection(self, connection):
        VTKPythonAlgorithmBase.SetInputConnection(self, 0, connection)
        self.ex.SetInputConnection(0, connection)

    def set_selection(self, selection):
        self.selection_set = selection
        self.Modified()

    def set_array_name(self, array_name):
        self.selection_list.SetName(array_name)
        self.Modified()

    def pre_filter(self, ugrid):
        self.selection_list.Reset()

        cell_data = ugrid.GetCellData()
        arr = cell_data.GetArray(self.selection_list.GetName())
        get_value = arr.GetValue

        selection_set = self.selection_set.to_set()
        insert_value = self.selection_list.InsertNextValue

        for i in range(arr.GetNumberOfTuples()):
            if get_value(i) in selection_set:
                insert_value(i)

    def RequestData(self, request, inInfo, outInfo):
        inp = vtk.vtkUnstructuredGrid.GetData(inInfo[0])

        if inp is None or inp.GetNumberOfCells() == 0:
            debuginfo('no input!')
            return 1

        self.pre_filter(inp)

        #self.ex.SetInputDataObject(0, inp)
        self.ex.Modified()
        self.ex.Update()

        opt = vtk.vtkUnstructuredGrid.GetData(outInfo.GetInformationObject(0))
        opt.ShallowCopy(self.ex.GetOutputDataObject(0))

        debuginfo(opt.GetPoints())

        return 1
