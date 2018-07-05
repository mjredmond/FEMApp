from __future__ import print_function, absolute_import

import vtk

from fem.model.bdf.card_info_list import CardInfoList
from .ugrid import UGrid

card_info = CardInfoList.instance()


def ugrid_from_nastran(ugrid):
    # type(UGrid)->None

    cell_data = ugrid.GetCellData()

    card_ids = vtk.vtkVariantArray()
    card_ids.SetName('card_ids')
    global_ids_0 = vtk.vtkIntArray()
    global_ids_0.SetName('global_ids_0')
    global_ids = vtk.vtkIntArray()
    global_ids.SetName('global_ids')
    original_ids = vtk.vtkIntArray()
    original_ids.SetName('original_ids')
    visible = vtk.vtkIntArray()
    visible.SetName('visible')
    card_categories = vtk.vtkIntArray()
    card_categories.SetName('card_categories')
    card_types = vtk.vtkIntArray()
    card_types.SetName('card_types')

    cell_data.AddArray(card_ids)
    cell_data.AddArray(global_ids_0)
    cell_data.AddArray(global_ids)
    cell_data.AddArray(original_ids)
    cell_data.AddArray(visible)
    cell_data.AddArray(card_categories)
    cell_data.AddArray(card_types)

    element_id = cell_data.GetArray('element_id')

    elem_types = ugrid.elem_types

    cell_count = ugrid.GetNumberOfCells()
    card_ids.SetNumberOfValues(cell_count)
    global_ids_0.SetNumberOfValues(cell_count)
    global_ids.SetNumberOfValues(cell_count)
    original_ids.SetNumberOfValues(cell_count)
    visible.SetNumberOfValues(cell_count)
    card_categories.SetNumberOfValues(cell_count)
    card_types.SetNumberOfValues(cell_count)

    for i in range(ugrid.GetNumberOfCells()):
        elem_type = elem_types[i]

        elem_id = element_id.GetValue(i)

        card_info_obj = card_info.get_data(elem_type)
        category = card_info_obj.category
        category_index = card_info.categories(category)
        card_index = card_info_obj.index

        global_id = card_info.from_global_id(elem_id, category_index)

        card_ids.SetValue(i, elem_type)
        global_ids_0.SetValue(i, elem_id)
        global_ids.SetValue(i, global_id)
        original_ids.SetValue(i, i)
        visible.SetValue(i, 1)
        card_categories.SetValue(i, category_index)
        card_types.SetValue(i, card_index)
