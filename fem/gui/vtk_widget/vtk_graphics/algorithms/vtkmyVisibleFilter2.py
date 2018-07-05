from __future__ import print_function, absolute_import

import vtk
from typing import List, Set
from vtk.util import numpy_support
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase


class vtkmyVisibleFilter2(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkUnstructuredGrid',
                                        nOutputPorts=1, outputType='vtkUnstructuredGrid')

        self.selection_list = vtk.vtkIntArray()
        self.selection_node = vtk.vtkSelectionNode()
        self.selection = vtk.vtkSelection()
        self.ex = vtk.vtkExtractSelection()

        self.active_groups = set()
        self.active_types = set()
        self.visible_ids = set()
        self.visible_on = True

        self.selection_list.SetName('visible')
        self.selection_list.SetNumberOfValues(2)
        self.selection_list.SetValue(0, 1)
        self.selection_list.SetValue(1, 1)

        self.selection_node.SetContentType(vtk.vtkSelectionNode.THRESHOLDS)
        self.selection_node.SetSelectionList(self.selection_list)
        self.selection.AddNode(self.selection_node)
        self.ex.ReleaseDataFlagOn()
        self.ex.SetInputDataObject(1, self.selection)

    def RequestData(self, request, inInfo, outInfo):
        # print('vtkmyVisibleFilter2.RequestData')
        inp = vtk.vtkUnstructuredGrid.GetData(inInfo[0])
        opt = vtk.vtkUnstructuredGrid.GetData(outInfo.GetInformationObject(0))

        if not inp or inp.GetNumberOfCells() == 0:
            opt.ShallowCopy(inp)
            return 1

        # print('pre_filter')
        self.pre_filter(inp)
        # print('pre_filter done!')

        # print(1)
        self.ex.SetInputData(0, inp)
        # print(2)
        self.ex.Modified()
        # print(3)
        self.ex.Update()

        new_opt = self.ex.GetOutputDataObject(0)

        # print(new_opt)

        # print(4)
        opt.DeepCopy(new_opt)  # was doing a ShallCopy a while back, but it crashes now for some reason

        # print('vtkmyVisibleFilter2.RequestData done!')

        return 1

    def pre_filter(self, ugrid):
        if not (self.active_groups and self.active_types and self.visible_ids):
            return

        cell_data = ugrid.GetCellData()

        if not cell_data.HasArray('global_ids'):
            return

        global_ids = cell_data.GetArray('global_ids')
        card_types = cell_data.GetArray('card_types')
        visible = cell_data.GetArray('visible')

        for i in range(ugrid.GetNumberOfCells()):
            global_id = global_ids.GetValue(i)
            card_type = card_types.GetValue(i)

            if global_id in self.active_groups and card_type in self.active_types:
                if global_id in self.visible_ids:
                    visible.SetValue(i, 1)
                else:
                    visible.SetValue(i, -1)
            else:
                visible.SetValue(i, -2)

    def set_active_groups(self, groups):
        assert hasattr(groups, '__contains__'), groups
        self.active_groups = groups
        self.Modified()

    def set_active_types(self, types):
        assert hasattr(types, '__contains__'), types
        self.active_types = types
        self.Modified()

    def set_visible_ids(self, ids):
        assert hasattr(ids, '__contains__'), ids
        self.visible_ids = ids
        self.Modified()

    def toggle_visible(self):
        if self.visible_on:
            self.visible_on = False
            self.selection_list.SetValue(0, -1)
            self.selection_list.SetValue(1, -1)
        else:
            self.visible_on = True
            self.selection_list.SetValue(0, 1)
            self.selection_list.SetValue(1, 1)

        self.selection.Modified()
        self.Modified()
        self.InvokeEvent('filter_modified')
