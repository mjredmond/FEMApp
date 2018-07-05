from __future__ import print_function, absolute_import

import vtk


class vtkPVInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        #vtk.vtkInteractorStyleTrackballCamera.__init__(self)

        self.SetUseTimers(0)
        self.CameraManipulators = []
        self.CurrentManipulator = None
        self.CenterOfRotation = [0., 0., 0.]
        self.RotationFactor = 1.
        self.ZoomScaleFactor = 1.
        self.TranslationFactor = 1.

        self.AddObserver("MouseMoveEvent", self._OnMouseMove)
        self.AddObserver("LeftButtonPressEvent", self._OnLeftButtonDown)
        self.AddObserver("LeftButtonReleaseEvent", self._OnLeftButtonUp)
        self.AddObserver("MiddleButtonPressEvent", self._OnMiddleButtonDown)
        self.AddObserver("MiddleButtonReleaseEvent", self._OnMiddleButtonUp)
        self.AddObserver("RightButtonPressEvent", self._OnRightButtonDown)
        self.AddObserver("RightButtonReleaseEvent", self._OnRightButtonUp)
        self.AddObserver("KeyPressEvent", self._OnKeyDown)
        self.AddObserver("KeyReleaseEvent", self._OnKeyUp)

        self._down_pos = None
        self._up_pos = None

    def RemoveAllManipulators(self):
        self.CameraManipulators = []

    def AddManipulator(self, m):
        self.CameraManipulators.append(m)

    def OnButtonDown(self, button, shift, control):
        if self.CurrentManipulator:
            return

        interactor = self.GetInteractor()
        event_pos = interactor.GetEventPosition()
        self._down_pos = event_pos

        self.FindPokedRenderer(event_pos[0], event_pos[1])

        current_renderer = self.GetCurrentRenderer()

        if not current_renderer:
            return

        self.CurrentManipulator = self.FindManipulator(button, shift, control)

        if self.CurrentManipulator:
            self.CurrentManipulator.Register(self)
            self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent)
            self.CurrentManipulator.SetCenter(self.CenterOfRotation)
            self.CurrentManipulator.SetRotationFactor(self.RotationFactor)
            self.CurrentManipulator.SetZoomScaleFactor(self.ZoomScaleFactor)
            self.CurrentManipulator.SetTranslationFactor(self.TranslationFactor)
            self.CurrentManipulator.StartInteraction()
            self.CurrentManipulator.OnButtonDown(event_pos[0], event_pos[1], current_renderer, interactor)

    def OnButtonUp(self, button):
        if not self.CurrentManipulator:
            return

        interactor = self.GetInteractor()
        event_pos = interactor.GetEventPosition()
        self._up_pos = event_pos

        if self.CurrentManipulator.Button == button:
            self.CurrentManipulator.OnButtonUp(event_pos[0], event_pos[1], self.GetCurrentRenderer(), interactor)
            self.CurrentManipulator.EndInteraction()
            self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent)
            self.CurrentManipulator.UnRegister(self)
            self.CurrentManipulator = None

    def FindManipulator(self, button, shift, control):
        for m in self.CameraManipulators:
            try:
                if m.GetButton() == button and m.GetShift() == shift and m.GetControl() == control:
                    return m
            except AttributeError:
                print(m)
                print(type(m))
                print(dir(m))

        return None

    def ResetLights(self):
        pass

    def _OnLeftButtonDown(self, *args):
        interactor = self.GetInteractor()
        self.OnButtonDown(1, interactor.GetShiftKey(), interactor.GetControlKey())

    def _OnMiddleButtonDown(self, *args):
        interactor = self.GetInteractor()
        self.OnButtonDown(2, interactor.GetShiftKey(), interactor.GetControlKey())

    def _OnRightButtonDown(self, *args):
        interactor = self.GetInteractor()
        self.OnButtonDown(3, interactor.GetShiftKey(), interactor.GetControlKey())

    def _OnLeftButtonUp(self, *args):
        self.OnButtonUp(1)

    def _OnMiddleButtonUp(self, *args):
        self.OnButtonUp(2)

    def _OnRightButtonUp(self, *args):
        self.OnButtonUp(3)

    def _OnMouseMove(self, *args):
        current_renderer = self.GetCurrentRenderer()
        current_manipulator = self.CurrentManipulator

        interactor = self.GetInteractor()
        event_pos = interactor.GetEventPosition()

        if not (current_manipulator and current_renderer):
            self.FindPokedRenderer(event_pos[0], event_pos[1])
            current_renderer = self.GetCurrentRenderer()
            current_manipulator = self.CurrentManipulator

        if current_manipulator and current_renderer:
            current_manipulator.OnMouseMove(event_pos[0], event_pos[1], current_renderer, interactor)
            self.InvokeEvent(vtk.vtkCommand.InteractionEvent)

    def _OnChar(self, *args):
        rwi = self.GetInteractor()

        key_code = rwi.GetKeyCode()

        if key_code == 'q':
            rwi.ExitCallback()

    def _OnKeyDown(self, *args):
        interactor = self.GetInteractor()
        for m in self.CameraManipulators:
            m.OnKeyDown(interactor)

    def _OnKeyUp(self, *args):
        interactor = self.GetInteractor()
        for m in self.CameraManipulators:
            m.OnKeyUp(interactor)

