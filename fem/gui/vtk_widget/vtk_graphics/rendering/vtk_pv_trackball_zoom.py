from __future__ import print_function, absolute_import

import numpy as np
import vtk

from .vtk_camera_manipulator import vtkCameraManipulator

np_array = np.array
np_cross = np.cross


class vtkPVTrackballZoom(vtkCameraManipulator):
    def __init__(self):
        vtkCameraManipulator.__init__(self)
        self.ZoomScale = 1.

    def OnButtonDown(self, x, y, ren, iren):
        size = ren.GetSize()
        camera = ren.GetActiveCamera()

        if camera.GetParallelProjection():
            self.ZoomScale = 3.*self.ZoomScaleFactor/size[1]
        else:
            range = camera.GetClippingRange()
            self.ZoomScale = self.ZoomScaleFactor*range[1]/size[1]

    def OnMouseMove(self, x, y, ren, iren):
        dy = iren.GetLastEventPosition()[1] - y
        camera = ren.GetActiveCamera()

        if camera.GetParallelProjection():
            k = dy*self.ZoomScale
            camera.SetParallelScale((1. - k)*camera.GetParallelScale())
        else:
            pos = list(camera.GetPosition())
            fp = list(camera.GetFocalPoint())
            norm = camera.GetDirectionOfProjection()
            k = dy*self.ZoomScale

            tmp = k*norm[0]
            pos[0] += tmp
            fp[0] += tmp

            tmp = k*norm[1]
            pos[1] += tmp
            fp[1] += tmp

            tmp = k*norm[2]
            pos[2] += tmp
            fp[2] += tmp

            if not camera.GetFreezeFocalPoint():
                camera.SetFocalPoint(fp)

            camera.SetPosition(pos)
            ren.ResetCameraClippingRange()

        iren.Render()

    def PrintSelf(self):
        super(self, vtkPVTrackballZoom).PrintSelf()
        print("ZoomScale: %f" % self.ZoomScale)