from __future__ import print_function, absolute_import

import numpy as np
import vtk
from collections import defaultdict
from itertools import chain
from six import itervalues
from vtk.util.numpy_support import numpy_to_vtk


def _basic_elem(elem, cell_type, ugrid, nid_dict):
    nids = [nid_dict[nid] for nid in elem.node_ids]

    ids = vtk.vtkIdList()
    ids.SetNumberOfIds(len(nids))

    for i in range(len(nids)):
        ids.SetId(i, nids[i])

    ugrid.InsertNextCell(cell_type, ids)

    return elem.eid


def _grid(grid, cell_type, ugrid, nid_dict):
    nids = [nid_dict[nid] for nid in [grid.nid]]

    ids = vtk.vtkIdList()
    ids.SetNumberOfIds(len(nids))

    for i in range(len(nids)):
        ids.SetId(i, nids[i])

    ugrid.InsertNextCell(cell_type, ids)

    return grid.nid


def _rbe2(elem, cell_type, ugrid, nid_dict):
    independent = elem.gn

    dependent = elem.Gmi

    nids = []

    for i in range(len(dependent)):
        nids.append(nid_dict[independent])
        nids.append(nid_dict[dependent[i]])

    ids = vtk.vtkIdList()
    ids.SetNumberOfIds(len(nids))

    for i in range(len(nids)):
        ids.SetId(i, nids[i])

    ugrid.InsertNextCell(cell_type, ids)

    return elem.eid


def _rbe3(elem, cell_type, ugrid, nid_dict):
    independent = elem.refgrid
    _dependent = elem.Gijs

    dependent = []

    for dep in _dependent:
        if isinstance(dep, list):
            dependent.extend(dep)
        else:
            dependent.append(dep)

    nids = []

    for i in range(len(dependent)):
        nids.append(nid_dict[independent])
        nids.append(nid_dict[dependent[i]])

    ids = vtk.vtkIdList()
    ids.SetNumberOfIds(len(nids))

    for i in range(len(nids)):
        ids.SetId(i, nids[i])

    ugrid.InsertNextCell(cell_type, ids)

    return elem.eid


_category_list = ['grid', 'element', 'mpc', 'force', 'disp', 'cord']

_nastran_to_vtk = {
    'GRID': (vtk.VTK_VERTEX, _grid, 'grid'),
    'CQUAD4': (vtk.VTK_QUAD, _basic_elem, 'element'),
    'CTRIA3': (vtk.VTK_TRIANGLE, _basic_elem, 'element'),
    'CBEAM': (vtk.VTK_LINE, _basic_elem, 'element'),
    'CBUSH': (vtk.VTK_LINE, _basic_elem, 'element'),
    'CBAR': (vtk.VTK_LINE, _basic_elem, 'element'),
    'RBE2': (vtk.VTK_POLY_LINE, _rbe2, 'mpc'),
    'RBE3': (vtk.VTK_POLY_LINE, _rbe3, 'mpc')
}

_card_types = {}

i = 0
for key in sorted(_nastran_to_vtk.keys()):
    _card_types[key] = i
    i += 1


class UGrid(vtk.vtkUnstructuredGrid):
    category_list = _category_list
    category_dict = {_category_list[i]: i for i in range(len(_category_list))}

    nastran_to_vtk = _nastran_to_vtk
    card_types = _card_types

    @classmethod
    def make_from_bdf(cls, bdf):
        # type: (BDF) -> UGrid

        nid_list = []
        nid_dict = {}

        node_pos = np.empty((len(bdf.nodes), 3), dtype=np.float64)

        i = 0
        for node in itervalues(bdf.nodes):
            node_pos[i] = node.get_position()
            nid = node.nid
            nid_list.append(nid)
            nid_dict[nid] = i
            i += 1

        _points = vtk.vtkPoints()
        _points.SetData(numpy_to_vtk(node_pos))

        points = vtk.vtkPoints()
        points.DeepCopy(_points)

        cells = []
        cell_types = []
        cell_count = 0
        elem_types = []

        eid_list = []

        _nastran_to_vtk = cls.nastran_to_vtk

        bdf_data_to_plot = chain(
            itervalues(bdf.nodes),
            itervalues(bdf.elements),
            itervalues(bdf.rigid_elements)
        )

        category_list = []
        category_dict = cls.category_dict

        ugrid = vtk.vtkUnstructuredGrid()
        ugrid.SetPoints(points)

        for elem in bdf_data_to_plot:
            elem_type = elem.type
            cell_type, add_method, category = _nastran_to_vtk.get(elem_type, (None, None, None))

            if cell_type is None:
                continue

            cell_types.append(cell_type)
            elem_types.append(elem_type)

            eid = add_method(elem, cell_type, ugrid, nid_dict)  # returns element/grid id

            eid_list.append(eid)

            category_list.append(category_dict[category])

            cell_count += 1

        id_array = numpy_to_vtk(np.array(cells, dtype=np.int64), deep=1, array_type=vtk.VTK_ID_TYPE)

        vtk_cells = vtk.vtkCellArray()
        vtk_cells.SetCells(cell_count, id_array)

        cell_types = np.array(cell_types, 'B')
        vtk_cell_types = numpy_to_vtk(cell_types)

        cell_locations = np.array([i for i in range(cell_count)])
        vtk_cell_locations = numpy_to_vtk(cell_locations, deep=1, array_type=vtk.VTK_ID_TYPE)

        vtk_cell_locations.SetName('index')
        ugrid.GetCellData().AddArray(vtk_cell_locations)

        _elem_types = vtk.vtkIdTypeArray()
        _elem_types.SetName('element_type')
        _elem_types.SetNumberOfValues(len(elem_types))

        card_types = cls.card_types

        for i in range(len(elem_types)):
            _elem_types.SetValue(i, card_types[elem_types[i]])

        ugrid.GetCellData().AddArray(_elem_types)

        _cat = numpy_to_vtk(np.array(category_list, dtype=np.int64), deep=1, array_type=vtk.VTK_ID_TYPE)
        _cat.SetName('category')

        ugrid.GetCellData().AddArray(_cat)

        id_array = numpy_to_vtk(np.array(eid_list, dtype=np.int64), deep=1, array_type=vtk.VTK_ID_TYPE)
        id_array.SetName('element_id')

        ugrid.GetCellData().AddArray(id_array)

        copy = cls()
        copy.DeepCopy(ugrid)
        copy.update()
        copy._nid_dict = nid_dict
        copy._nid_list = nid_list
        copy.elem_types.extend(elem_types)

        return copy

    def __init__(self, *args, **kwargs):
        vtk.vtkUnstructuredGrid.__init__(self, *args, **kwargs)

        self._category = []
        self._elem_type = defaultdict(set)
        self._elem_to_index = defaultdict(set)
        self._nid_list = []
        self._nid_dict = {}
        self.elem_types = []

    def num_to_card_type(self, num):
        return self.card_types.get(num, None)

    def update(self):
        category = self.GetCellData().GetArray('category')
        elem_type = self.GetCellData().GetArray('element_type')
        elem_id = self.GetCellData().GetArray('element_id')

        _category = [set(), set(), set(), set(), set(), set()]
        _elem_type = defaultdict(set)
        _elem_to_index = defaultdict(set)

        get_category = category.GetValue
        get_elem_type = elem_type.GetValue
        get_elem_id = elem_id.GetValue

        for i in range(category.GetNumberOfValues()):
            _category[get_category(i)].add(i)
            _elem_type[get_elem_type(i)].add(i)
            _elem_to_index[get_elem_id(i)].add(i)

        del self._category[:]
        self._category.extend(_category)

        self._elem_type.clear()
        self._elem_type.update(_elem_type)

        self._elem_to_index.clear()
        self._elem_to_index.update(_elem_to_index)

    def get_category_indices(self, category):
        if isinstance(category, str):
            category = self.category_dict[category]
        return self._category[category]

    def get_element_type_indices(self, elem_type):
        return self._elem_type[elem_type]

    def get_eid_indices(self, eids):
        result = set()
        _elem_to_index = self._elem_to_index

        for eid in eids:
            result.update(_elem_to_index[eid])

        category = self.category_dict['element']
        category_indices = self._category[category]
        return result.intersection(category_indices)

    def get_eid_index(self, eid):
        category = self.category_dict['element']
        category_indices = self._category[category]
        index = self._elem_to_index[eid].intersection(category_indices)
        assert len(index) == 1, (eid, index)
        return list(index)[0]

    def visualize(self):
        ugrid = self

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(ugrid)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        renderer = vtk.vtkRenderer()
        rw = vtk.vtkRenderWindow()
        rw.AddRenderer(renderer)

        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(rw)
        renderer.AddActor(actor)

        interactor_style = vtk.vtkInteractorStyleTrackballCamera()

        iren.SetInteractorStyle(interactor_style)

        lut = vtk.vtkLookupTable()
        lut.SetHueRange(2 / 3, 0)
        lut.Build()

        mapper.SetLookupTable(lut)
        # actor.GetProperty().SetRepresentationToWireframe()

        iren.Initialize()
        rw.Render()
        iren.Start()
