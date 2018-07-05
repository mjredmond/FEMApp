from __future__ import print_function, absolute_import

import vtk


class vtkCameraManipulatorGUIHelper(vtk.vtkObject):
    def __init__(self):
        pass

    def UpdateGUI(self):
        return 0

    def GetActiveSourceBounds(self, bounds):
        return 0

    def GetActiveActorTranslate(self, translate):
        return 0

    def SetActiveActorTranslate(self, translate):
        return 0

    def GetCenterOfRotation(self, center):
        return 0

    def PrintSelf(self):
        pass