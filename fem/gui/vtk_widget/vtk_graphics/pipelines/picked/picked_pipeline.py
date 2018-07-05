from __future__ import print_function, absolute_import

import vtk


class PickedPipeline(object):
    def __init__(self):
        # visible_filter determines what is shown on the screen
        self.filter = None

        self.mapper = vtk.vtkDataSetMapper()

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(self.actor)

        self.actor.GetProperty().EdgeVisibilityOn()
        self.actor.GetProperty().SetColor(0, 0.5, 0.5)
        self.actor.GetProperty().SetLineWidth(1)
        self.actor.GetProperty().SetPointSize(6)
        self.actor.GetProperty().SetRepresentationToWireframe()
        self.actor.GetProperty().LightingOff()
        #self.actor.GetProperty().SetOpacity(0.5)

    def set_filter(self, filter):
        self.filter = filter
        self.mapper.SetInputConnection(self.filter.GetOutputPort())

    def finalize(self):
        self.renderer.RemoveActor(self.actor)
        self.actor = None
        self.mapper.RemoveAllInputConnections(0)
        self.mapper = None
        self.renderer = None
