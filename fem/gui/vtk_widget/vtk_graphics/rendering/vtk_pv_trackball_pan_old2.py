from __future__ import print_function, absolute_import

import numpy as np
import vtk
from vtk_camera_manipulator import vtkCameraManipulator

np_array = np.array
np_cross = np.cross


class vtkPVTrackballPan2(vtkCameraManipulator):
    def __init__(self):
        vtkCameraManipulator.__init__(self)

        self._interactor_style = vtk.vtkInteractorStyleTrackballCamera()

    def OnMouseMove(self, x, y, ren, iren):
        self._interactor_style.SetInteractor(iren)
        self._interactor_style.SetCurrentRenderer(ren)
        self._interactor_style.OnMouseMove()

    def OnButtonDown(self, x, y, ren, iren):
        self._interactor_style.SetInteractor(iren)
        self._interactor_style.SetCurrentRenderer(ren)
        self._interactor_style.OnMiddleButtonDown()

    def OnButtonUp(self, x, y, ren, iren):
        self._interactor_style.SetInteractor(iren)
        self._interactor_style.SetCurrentRenderer(ren)
        self._interactor_style.OnMiddleButtonUp()

    def OnKeyUp(self, iren):
        self._interactor_style.SetInteractor(iren)
        self._interactor_style.OnKeyUp()

    def OnKeyDown(self, iren):
        self._interactor_style.SetInteractor(iren)
        self._interactor_style.OnKeyDown()