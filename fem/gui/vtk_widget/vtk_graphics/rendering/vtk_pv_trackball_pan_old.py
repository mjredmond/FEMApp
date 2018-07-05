from __future__ import print_function, absolute_import

import numpy as np
import vtk
from vtkCameraManipulator import vtkCameraManipulator

np_array = np.array
np_cross = np.cross


class vtkPVTrackballPan(vtkCameraManipulator):
    def OnMouseMove(self, x, y, ren, iren):
        if ren is None or not self.GUIHelper:
            return

        camera = ren.GetActiveCamera()
        pos = list(camera.GetPosition())
        fp = list(camera.GetFocalPoint())

        if camera.GetParallelProjection():
            camera.OrthogonalizeViewUp()
            up = np_array(camera.GetViewUp())
            vpn = np_array(camera.GetViewPlaneNormal())
            right = np_cross(up, vpn)

            size = ren.GetSize()
            last_pos = iren.GetLastEventPosition()
            dx = (x - last_pos[0])/size[1]
            dy = (last_pos[1] - y)/size[1]

            scale = camera.GetParallelScale()
            dx *= scale*2.
            dy *= scale*2.

            tmp = (right[0]*dx + up[0]*dy)
            pos[0] += tmp
            fp[0] += tmp

            tmp = (right[1]*dx + up[1]*dy)
            pos[1] += tmp
            fp[1] += tmp

            tmp = (right[2]*dx + up[2]*dy)
            pos[2] += tmp
            fp[2] += tmp

            camera.SetPosition(pos)
            camera.SetFocalPoint(pos)

        else:
            bounds = [0, 0, 0, 0, 0, 0]
            center = [0, 0, 0]

            if self.GUIHelper.GetActiveSourceBounds(bounds):
                center[0] = (bounds[0] + bounds[1])/2.
                center[1] = (bounds[2] + bounds[3])/2.
                center[2] = (bounds[4] + bounds[5])/2.
                ren.SetWorldPoint(center[0], center[1], center[2], 1.)
            else:
                if self.GUIHelper.GetCenterOfRotation(center):
                    ren.SetWorldPoint(center[0], center[1], center[2], 1.)

            ren.WorldToDisplay()
            depth = ren.GetDisplayPoint()[2]

            ren.SetDisplayPoint(x, y, depth)
            ren.DisplayToWorld()
            worldPt = list(ren.GetWorldPoint())

            if worldPt[3]:
                worldPt3 = worldPt[3]
                worldPt[0] /= worldPt3
                worldPt[1] /= worldPt3
                worldPt[2] /= worldPt3
                worldPt[3] = 1.

            last_pos = iren.GetLastEventPosition()
            ren.SetDisplayPoint(last_pos[0], last_pos[1], depth)
            ren.DisplayToWorld()
            lastWorldPt = list(ren.GetWorldPoint())

            if lastWorldPt[3]:
                lastWorldPt3 = lastWorldPt[3]
                lastWorldPt[0] /= lastWorldPt3
                lastWorldPt[1] /= lastWorldPt3
                lastWorldPt[2] /= lastWorldPt3
                lastWorldPt[3] = 1.

            diff0 = lastWorldPt[0] - worldPt[0]
            diff1 = lastWorldPt[1] - worldPt[1]
            diff2 = lastWorldPt[2] - worldPt[2]

            pos[0] += diff0
            pos[1] += diff1
            pos[2] += diff2

            fp[0] += diff0
            fp[1] += diff1
            fp[2] += diff2

            camera.SetPosition(pos)
            camera.SetFocalPoint(fp)

        ren.ResetCameraClippingRange()
        iren.Render()