from __future__ import print_function, absolute_import

# from vtk_fem.fem_data import fem_data
from fem.utilities import MrSignal
from fem.gui.vtk_widget.vtk_graphics.algorithms.vtkmyArrayValueFilter2 import vtkmyArrayValueFilter2


class PickedFilter(vtkmyArrayValueFilter2):
    def __init__(self):
        vtkmyArrayValueFilter2.__init__(self)

        #self.set_selection(selection.raw_pointer())

        #self.filter_modified = MrSignal()

        #selection_data.picked_data_changed.connect(self._data_changed)

    #def _data_changed(self):
    #    self.set_selection(selection_data.picked.raw_pointer())
    #    self.filter_modified.emit()
    #    selection_data.render()
