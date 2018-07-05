from __future__ import print_function, absolute_import

import numpy as np
import vtk

from .vtk_camera_manipulator import vtkCameraManipulator

np_array = np.array
np_cross = np.cross

vtkMath_Norm = vtk.vtkMath.Norm

from fem.utilities.debug import show_stack_trace


class vtkPVTrackballRotate(vtkCameraManipulator):
    def __init__(self):
        vtkCameraManipulator.__init__(self)

    def OnButtonDown(self, x, y, ren, iren):
        self._ComputeDisplayCenter(ren)

    def OnMouseMove(self, x, y, ren, iren):
        if not ren:
            return

        transform = vtk.vtkTransform()
        camera = ren.GetActiveCamera()

        scale = vtkMath_Norm(camera.GetPosition())
        if scale <= 0.:
            scale = vtkMath_Norm(camera.GetFocalPoint())
            if scale <= 0.:
                scale = 1.

        temp = camera.GetFocalPoint()
        camera.SetFocalPoint(temp[0]/scale, temp[1]/scale, temp[2]/scale)
        temp = camera.GetPosition()
        camera.SetPosition(temp[0]/scale, temp[1]/scale, temp[2]/scale)

        center = self.Center

        transform.Identity()
        transform.Translate(center[0]/scale, center[1]/scale, center[2]/scale)

        last_pos = iren.GetLastEventPosition()

        dx = last_pos[0] - x
        dy = last_pos[1] - y

        camera.OrthogonalizeViewUp()
        size = ren.GetSize()

        try:
            key_code = self.KeyCode.upper()
        except AttributeError:
            key_code = self.KeyCode

        if key_code in ['X', 'Y', 'Z']:
            use_dx = abs(dx) > abs(dy)

            if use_dx:
                delta = 360.*dx/size[0]
            else:
                delta = -360.*dy/size[1]

            axis = [0., 0., 0.]

            if key_code == 'X':
                axis[0] = 1.
            elif key_code == 'Y':
                axis[1] = 1.
            elif key_code == 'Z':
                axis[2] = 1.
            else:
                raise Exception

            transform.RotateWXYZ(delta, axis[0], axis[1], axis[2])

        else:
            viewUp = camera.GetViewUp()
            transform.RotateWXYZ(360.*dx/size[0]*self.RotationFactor, viewUp[0], viewUp[1], viewUp[2])

            v2 = np_cross(np_array(camera.GetDirectionOfProjection()), np_array(viewUp))
            transform.RotateWXYZ(-360.*dy/size[1]*self.RotationFactor, v2[0], v2[1], v2[2])

        transform.Translate(-center[0]/scale, -center[1]/scale, -center[2]/scale)

        camera.ApplyTransform(transform)
        camera.OrthogonalizeViewUp()

        temp = camera.GetFocalPoint()
        camera.SetFocalPoint(temp[0]*scale, temp[1]*scale, temp[2]*scale)
        temp = camera.GetPosition()
        camera.SetPosition(temp[0]*scale, temp[1]*scale, temp[2]*scale)

        ren.ResetCameraClippingRange()

        iren.Render()

    def PrintSelf(self):
        super(self, vtkPVTrackballRotate).PrintSelf()
        print("Center: %f, %f, %f" % (self.Center[0], self.Center[1], self.Center[2]))