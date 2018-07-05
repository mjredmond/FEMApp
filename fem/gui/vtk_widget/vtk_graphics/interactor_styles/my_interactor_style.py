from __future__ import print_function, absolute_import

import vtk

from fem.utilities import MrSignal
from ..picking import PickingManager
from ...vtk_graphics import VTKGraphics
from ...vtk_graphics.rendering import (
    vtkPVInteractorStyle, vtkPVTrackballPan, vtkPVTrackballRotate, vtkPVTrackballZoom, vtkCameraManipulator,
    vtkCameraManipulatorGUIHelper
)


class MyInteractorStyle(vtkPVInteractorStyle):
    def __init__(self):
        vtkPVInteractorStyle.__init__(self)

        self._rotate = vtkPVTrackballRotate()
        self._pan = vtkPVTrackballPan()
        self._zoom = vtkPVTrackballZoom()

        self._hover = None
        """:type: gui.vtk_widget.vtk_graphics.interactor_styles.hovered_interactor_style.HoveredInteractorStyle"""

        self._pan.GUIHelper = vtkCameraManipulatorGUIHelper()

        self._buttons_pressed = set()

        # these need to be implemented
        #selection_data.translation_factor_changed.connect(self.set_translation_factor)
        #selection_data.rotation_factor_changed.connect(self.set_rotation_factor)
        #selection_data.zoom_scale_factor_changed.connect(self.set_zoom_scale_factor)

        self._box_picker = None
        """:type: gui.vtk_widget.vtk_graphics.picking.BoxPicker"""

        self._poly_picker = None
        """:type: gui.vtk_widget.vtk_graphics.picking.PolyPicker"""

        #selection_data.box_picker_activate.connect(self.box_picker_activate)
        #selection_data.poly_picker_activate.connect(self.poly_picker_activate)

        self._active_picker = None

        self.vtk_graphics = None
        """:type: VTKGRaphics"""

        self.picking_manager = None
        """:type: PickingManager"""

        self.zoom_changed = MrSignal()

    def build(self):

        self.AddManipulator(self._rotate)
        self.AddManipulator(self._pan)
        self.AddManipulator(self._zoom)
        self.AddManipulator(self._hover)

        self._rotate.Button = 1
        self._pan.Button = 2
        self._zoom.Button = 3
        self._hover.Button = -1

        self.vtk_graphics = VTKGraphics.instance()
        self.picking_manager = PickingManager.instance()

    def set_hover_interactor_style(self, hover):
        self._hover = hover

    def set_box_picker(self, box_picker):
        self._box_picker = box_picker
        self._box_picker.done_picking.connect(self._reset_mousemove)

    def set_poly_picker(self, poly_picker):
        self._poly_picker = poly_picker
        self._poly_picker.done_picking.connect(self._reset_mousemove)

    def box_picker_activate(self):
        self._active_picker = self._box_picker
        self._picker_activate()

    def poly_picker_activate(self):
        self._active_picker = self._poly_picker
        self._picker_activate()

    def _picker_activate(self):
        self.RemoveObservers("MouseMoveEvent")
        self.RemoveObservers("LeftButtonPressEvent")
        self.RemoveObservers("LeftButtonReleaseEvent")

        self.AddObserver("MouseMoveEvent", self._PickerOnMouseMove)
        self.AddObserver("LeftButtonPressEvent", self._PickerOnButtonDown)
        self.AddObserver("LeftButtonReleaseEvent", self._PickerOnButtonUp)

    def _reset_mousemove(self):
        self.picking_manager.picking_done()
        self.RemoveObservers("MouseMoveEvent")
        self.RemoveObservers("LeftButtonPressEvent")
        self.RemoveObservers("LeftButtonReleaseEvent")

        self.AddObserver("MouseMoveEvent", self._OnMouseMove)
        self.AddObserver("LeftButtonPressEvent", self._OnLeftButtonDown)
        self.AddObserver("LeftButtonReleaseEvent", self._OnLeftButtonUp)

    def _PickerOnMouseMove(self, *args):
        current_renderer = self.GetCurrentRenderer()

        interactor = self.GetInteractor()
        event_pos = interactor.GetEventPosition()

        if not current_renderer:
            self.FindPokedRenderer(event_pos[0], event_pos[1])
            current_renderer = self.GetCurrentRenderer()

        if current_renderer:
            self._active_picker.OnMouseMove(event_pos[0], event_pos[1], current_renderer, interactor)
            self.InvokeEvent(vtk.vtkCommand.InteractionEvent)

    def _PickerOnButtonDown(self, *args):
        current_renderer = self.GetCurrentRenderer()

        interactor = self.GetInteractor()
        event_pos = interactor.GetEventPosition()

        if not current_renderer:
            self.FindPokedRenderer(event_pos[0], event_pos[1])
            current_renderer = self.GetCurrentRenderer()

        self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent)
        self._active_picker.StartInteraction()
        self._active_picker.OnButtonDown(event_pos[0], event_pos[1], current_renderer, interactor)

    def _PickerOnButtonUp(self, *args):
        current_renderer = self.GetCurrentRenderer()

        interactor = self.GetInteractor()
        event_pos = interactor.GetEventPosition()

        if not current_renderer:
            self.FindPokedRenderer(event_pos[0], event_pos[1])
            current_renderer = self.GetCurrentRenderer()

        self._active_picker.OnButtonUp(event_pos[0], event_pos[1], current_renderer, interactor)
        self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent)

    def set_center_of_rotation(self, center):
        self.CenterOfRotation[:] = center[:]

    def set_translation_factor(self, factor):
        self.TranslationFactor = factor

    def set_rotation_factor(self, factor):
        self.RotationFactor = factor

    def set_zoom_scale_factor(self, factor):
        self.ZoomScaleFactor = factor

    def OnButtonDown(self, button, shift, control):
        if self.CurrentManipulator is self._hover:
            self.OnButtonUp(self._hover.Button)
            #self._hover.unload()

        if button > 0:
            self._buttons_pressed.add(button)

        vtkPVInteractorStyle.OnButtonDown(self, button, shift, control)

    def OnButtonUp(self, button):
        vtkPVInteractorStyle.OnButtonUp(self, button)

        if button > 0:
            try:
                self._buttons_pressed.remove(button)
            except KeyError:
                return

            if not self._buttons_pressed:
                old_down = self._down_pos
                vtkPVInteractorStyle.OnButtonDown(self, self._hover.Button, self._hover.Shift, self._hover.Control)
                self._down_pos = old_down

            if self._down_pos == self._up_pos:
                if self._hover.cell_picker.ClosestCellGlobalId > 0:
                    new_center = self._hover.cell_picker.CellCenter
                else:
                    new_center = None

                self.picking_manager.single_pick(
                    self._down_pos,
                    new_center,
                    self._hover.cell_picker.ClosestCellGlobalId
                )

    def finalize(self):
        self._box_picker.done_picking.disconnect(self._reset_mousemove)
        self._poly_picker.done_picking.disconnect(self._reset_mousemove)

        self._reset_mousemove()

        self._box_picker = None
        self._poly_picker = None
        self._active_picker = None

        self.RemoveAllManipulators()

        self._rotate = None
        self._pan = None
        self._zoom = None
        self._hover = None

        self.vtk_graphics = None
