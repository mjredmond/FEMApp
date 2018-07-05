from __future__ import print_function, absolute_import

import vtk


class CoordinateAxes(object):
    def __init__(self, interactor):
        super(CoordinateAxes, self).__init__()

        self.interactor = interactor

        self.axes = vtk.vtkAxesActor()
        self.axes_widget = vtk.vtkOrientationMarkerWidget()
        self.axes_widget.SetInteractor(self.interactor)
        self.axes_widget.SetOrientationMarker(self.axes)
        self.axes_widget.SetEnabled(1)
        self.axes_widget.SetOutlineColor(0.93, 0.57, 0.13)
        self.axes_widget.SetViewport(0., 0., 0.25, 0.25)
        self.axes_widget.InteractiveOff()
