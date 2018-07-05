from __future__ import print_function, absolute_import

from fem.utilities import MrSignal
from ...vtk_graphics import VTKGraphics


class SinglePicker(object):
    def __init__(self):
        self.vtk_graphics = VTKGraphics.instance()

        self.done = MrSignal()

    def pick(self, screen_pos, cell_pos, picked_global_id):
        raise NotImplementedError

    def finalize(self):
        self.vtk_graphics = None
