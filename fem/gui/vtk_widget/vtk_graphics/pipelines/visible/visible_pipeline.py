from __future__ import print_function, absolute_import

import vtk


class VisiblePipeline(object):
    def __init__(self):
        # visible_filter determines what is shown on the screen
        self.filter = None

        self.mapper = vtk.vtkDataSetMapper()

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(self.actor)

        self.actor.GetProperty().EdgeVisibilityOn()

    def set_filter(self, filter):
        self.filter = filter
        self.mapper.SetInputConnection(self.filter.GetOutputPort())

    def swap_visible(self):
        self.filter.toggle_visible()

    def finalize(self):
        self.renderer.RemoveActor(self.actor)
        self.actor = None
        self.mapper.RemoveAllInputConnections(0)
        self.mapper = None
        self.renderer = None
