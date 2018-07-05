from __future__ import print_function, absolute_import

import numpy as np
import vtk

from .vtk_camera_manipulator import vtkCameraManipulator

np_array = np.array
np_cross = np.cross


class vtkPVTrackballPan(vtkCameraManipulator):
    def __init__(self):
        vtkCameraManipulator.__init__(self)

    def OnMouseMove(self, x, y, ren, iren):
        if ren is None:
            return

        camera = ren.GetActiveCamera()
        viewFocus = list(camera.GetFocalPoint())
        self.ComputeWorldToDisplay(ren, viewFocus[0], viewFocus[1], viewFocus[2], viewFocus)

        focalDepth = viewFocus[2]

        event_pos = iren.GetEventPosition()

        newPickPoint = [0, 0, 0, 0]
        self.ComputeDisplayToWorld(ren, event_pos[0], event_pos[1], focalDepth, newPickPoint)

        last_pos = iren.GetLastEventPosition()
        oldPickPoint = [0, 0, 0, 0]
        self.ComputeDisplayToWorld(ren, last_pos[0], last_pos[1], focalDepth, oldPickPoint)

        try:
            key_code = self.KeyCode.upper()
        except AttributeError:
            key_code = self.KeyCode

        if key_code in ['X', 'Y', 'Z']:
            if key_code == 'X':
                axis_factors = [1., 0., 0.]
            elif key_code == 'Y':
                axis_factors = [0., 1., 0.]
            elif key_code == 'Z':
                axis_factors = [0., 0., 1.]
            else:
                raise Exception
        else:
            axis_factors = [1., 1., 1.]

        motionVector = [(oldPickPoint[0] - newPickPoint[0])*self.TranslationFactor*axis_factors[0],
                        (oldPickPoint[1] - newPickPoint[1])*self.TranslationFactor*axis_factors[1],
                        (oldPickPoint[2] - newPickPoint[2])*self.TranslationFactor*axis_factors[2]]

        viewFocus = camera.GetFocalPoint()
        viewPoint = camera.GetPosition()

        camera.SetFocalPoint(motionVector[0] + viewFocus[0],
                             motionVector[1] + viewFocus[1],
                             motionVector[2] + viewFocus[2])

        camera.SetPosition(motionVector[0] + viewPoint[0],
                           motionVector[1] + viewPoint[1],
                           motionVector[2] + viewPoint[2])

        if iren.GetLightFollowCamera():
            ren.UpdateLightsGeometryToFollowCamera()

        iren.Render()
