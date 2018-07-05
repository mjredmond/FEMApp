from __future__ import print_function, absolute_import

import vtk

from .vtkmyArrayValueFilter2 import vtkmyArrayValueFilter2


class PickableFilter(vtkmyArrayValueFilter2):
    def __init__(self):
        vtkmyArrayValueFilter2.__init__(self)
