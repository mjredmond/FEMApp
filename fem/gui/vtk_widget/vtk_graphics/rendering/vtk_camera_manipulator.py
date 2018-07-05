from __future__ import print_function, absolute_import

import vtk

from .vtk_camera_manipulator_gui_helper import vtkCameraManipulatorGUIHelper


class vtkCameraManipulator(vtk.vtkInteractorStyle):
    def __init__(self):
        self.ManipulatorName = self.__class__.__name__

        self.Button = 1
        self.Shift = 0
        self.Control = 0

        self.Center = [0., 0., 0.]
        self.DisplayCenter = [0., 0.]
        self.RotationFactor = 1.
        self.ZoomScaleFactor = 1.
        self.TranslationFactor = 1.

        self.KeyCode = 0

        self.GUIHelper = vtkCameraManipulatorGUIHelper()

    def GetButton(self):
        return self.Button

    def GetShift(self):
        return self.Shift

    def GetControl(self):
        return self.Control

    def SetButton(self, val):
        self.Button = val

    def SetShift(self, val):
        self.Shift = val

    def SetControl(self, val):
        self.Control = val

    def SetCenter(self, center):
        self.Center = center

    def GetCenter(self):
        return self.Center

    def SetRotationFactor(self, factor):
        self.RotationFactor = factor

    def SetZoomScaleFactor(self, factor):
        self.ZoomScaleFactor = factor

    def SetTranslationFactor(self, factor):
        self.TranslationFactor = factor

    def StartInteraction(self):
        pass

    def EndInteraction(self):
        pass

    def OnMouseMove(self, x, y, ren, iren):
        pass

    def OnButtonDown(self, x, y, ren, iren):
        pass

    def OnButtonUp(self, x, y, ren, iren):
        pass

    def OnKeyUp(self, iren):
        if iren.GetKeyCode() == self.KeyCode:
            self.KeyCode = 0

    def OnKeyDown(self, iren):
        if self.KeyCode == 0:
            self.KeyCode = iren.GetKeyCode()

    def _ComputeDisplayCenter(self, ren):
        center = self.Center
        ren.SetWorldPoint(center[0], center[1], center[2], 1.)
        ren.WorldToDisplay()
        pt = ren.GetDisplayPoint()
        self.DisplayCenter[0] = pt[0]
        self.DisplayCenter[1] = pt[1]

    def PrintSelf(self):
        print(self)
        print("ManipulatorName: %s" % self.ManipulatorName)
        print("Button: %d" % self.Button)
        print("Shift: %d" % self.Shift)
        print("Control: %d" % self.Control)
        print("Center: %f, %f, %f" % (self.Center[0], self.Center[1], self.Center[2]))
        print("RotationFactor: %f" % self.RotationFactor)
        print("GUIHelper: ")
        print(self.GUIHelper.PrintSelf())