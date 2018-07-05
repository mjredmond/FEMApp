from __future__ import print_function, absolute_import

import vtk
# noinspection PyUnresolvedReferences
from six.moves import range
from vtk.numpy_interface import dataset_adapter as dsa

from fem.utilities import BaseObject
from fem.utilities import MrSignal
from fem.utilities.debug import debuginfo
from .selection_data import FemSelection


# this is to suppress warnings when there are 0 cells for a vtk algorithm
# not the best way to do it, should prevent the warning instead
vtk.vtkObject.GlobalWarningDisplayOff()


class VTKGraphics(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(VTKGraphics, cls).__new__(cls)

        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, vtk_widget):
        super(VTKGraphics, self).__init__()

        self.vtk_widget = vtk_widget
        """:type: fem.gui.vtk_widget.VTKWidget"""

        self.render_window = self.vtk_widget.render_window

        self.interactor = self.vtk_widget.interactor

        self.data_source = None
        """:type: fem.gui.vtk_widget.vtk_graphics.algorithms.UnstructuredGridSource"""

        self.first_filter = None
        """:type: fem.gui.vtk_widget.vtk_graphics.algorithms.FirstFilter"""

        self.visible_types = None
        """:type: fem.gui.vtk_widget.vtk_graphics.selection_data.ActiveTypesSelection"""

        self.pickable_types = None
        """:type: fem.gui.vtk_widget.vtk_graphics.selection_data.ActiveTypesSelection"""

        self.bdf_card_info = None
        """:type: mrNastran.CardInfoList"""

        self.fem_groups = None
        """:type: fem.gui.vtk_widget.vtk_graphics.fem_group_list.FemGroupList"""

        self.visible_selection = None
        """:type: fem.gui.vtk_widget.vtk_graphics.visible.VisibleSelection"""

        self.hovered_selection = None
        """:type: fem.gui.vtk_widget.vtk_graphics.hovered.HoveredSelection"""

        self.picked_selection = None
        """:type: fem.gui.vtk_widget.vtk_graphics.picked.PickedSelection"""

        self.visible_filter = None
        """:type: fem.gui.vtk_widget.vtk_graphics.visible.VisibleFilter"""

        self.pickable_filter = None
        """:type: fem.gui.vtk_widget.vtk_graphics.algorithms.pickable_filter.PickableFilter"""

        self.picked_filter = None
        """:type: fem.gui.vtk_widget.vtk_graphics.picked.PickedFilter"""

        self.hovered_filter = None
        """:type: fem.gui.vtk_widget.vtk_graphics.hovered.HoveredFilter"""

        self.box_picker = None
        """:type: fem.gui.vtk_widget.vtk_graphics.picking.BoxPicker"""

        self.poly_picker = None
        """:type: fem.gui.vtk_widget.vtk_graphics.picking.PolyPicker"""

        self.hovered_interactor_style = None
        """:type: fem.gui.vtk_widget.vtk_graphics.interactor_styles.HoveredInteractorStyle"""

        self.interactor_style = None
        """:type: fem.gui.vtk_widget.vtk_graphics.interactor_styles.MyInteractorStyle"""

        self.visible_pipeline = None
        """:type: fem.gui.vtk_widget.vtk_graphics.visible.VisiblePipeline"""

        self.hovered_pipeline = None
        """:type: fem.gui.vtk_widget.vtk_graphics.hovered.HoveredPipeline"""

        self.picked_pipeline = None
        """:type: fem.gui.vtk_widget.vtk_graphics.picked.PickedPipeline"""

        self.coordinate_axes = None
        """:type: fem.gui.vtk_widget.utilities.CoordinateAxes"""

        self.camera = vtk.vtkCamera()
        self.camera.ParallelProjectionOn()
        self._perspective = 'parallel'

        self.bdf_data = None  # seems to be no longer used
        # FIXME: add type info

    def build(self):
        ##################################### BDF data source for VTK #####################################
        from fem.gui.vtk_widget.vtk_graphics.algorithms import UnstructuredGridSource
        self.data_source = UnstructuredGridSource()

        from fem.gui.vtk_widget.vtk_graphics.algorithms import FirstFilter
        self.first_filter = FirstFilter()
        self.first_filter.SetInputConnection(self.data_source.GetOutputPort())

        ##################################### Active Selection Types #####################################
        from fem.gui.vtk_widget.vtk_graphics.selection_data import ActiveTypesSelection

        self.visible_types = ActiveTypesSelection()
        self.visible_types.set_data(list(range(1000)))

        self.pickable_types = ActiveTypesSelection()
        self.pickable_types.set_data(list(range(1000)))

        ######################################################################################
        from fem.model.bdf.card_info_list import CardInfoList

        self.bdf_card_info = CardInfoList.instance()

        ######################################################################################
        from .fem_group_list import FemGroupList
        self.fem_groups = FemGroupList()
        self.fem_groups.data_changed.connect(self._groups_changed)

        ######################################################################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import VisibleSelection
        self.visible_selection = VisibleSelection()

        ######################################################################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import HoveredSelection
        self.hovered_selection = HoveredSelection()

        ######################################################################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import PickedSelection
        self.picked_selection = PickedSelection()

        ######################################################################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import VisibleFilter
        self.visible_filter = VisibleFilter()
        self.visible_filter.SetInputConnection(self.first_filter.GetOutputPort())
        self.visible_filter.set_visible_ids(self.visible_selection.raw_pointer())
        self.visible_filter.set_active_groups(self.fem_groups.all_groups().raw_pointer())
        self.visible_filter.set_active_types(self.visible_types.raw_pointer())

        ######################################################################################
        from .algorithms.pickable_filter import PickableFilter
        self.pickable_filter = PickableFilter()
        self.pickable_filter.SetInputConnection(self.visible_filter.GetOutputPort())
        self.pickable_filter.set_array_name(vtk.mutable("card_types"))
        self.pickable_filter.set_selection(self.pickable_types.raw_pointer())

        ######################################################################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import PickedFilter
        self.picked_filter = PickedFilter()
        self.picked_filter.set_selection(self.picked_selection.raw_pointer())
        self.picked_filter.SetInputConnection(self.visible_filter.GetOutputPort())

        ######################################################################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import HoveredFilter
        self.hovered_filter = HoveredFilter()
        self.hovered_filter.set_selection(self.hovered_selection.raw_pointer())
        self.hovered_filter.SetInputConnection(self.pickable_filter.GetOutputPort())

        ######################################################################################
        from .picking import BoxPicker
        self.box_picker = BoxPicker()
        self.box_picker.set_input_connection(self.pickable_filter.GetOutputPort())

        ######################################################################################
        from .picking import PolyPicker
        self.poly_picker = PolyPicker()
        self.poly_picker.set_input_connection(self.pickable_filter.GetOutputPort())

        ######################################################################################
        from .interactor_styles import HoveredInteractorStyle
        self.hovered_interactor_style = HoveredInteractorStyle()
        self.hovered_interactor_style.set_hovered_data(self.hovered_selection)
        self.hovered_interactor_style.set_visible_filter(self.visible_filter)
        self.hovered_interactor_style.set_pickable_types(self.pickable_types)
        self.hovered_interactor_style.key_down.connect(self._key_down)

        ######################################################################################
        from .interactor_styles import MyInteractorStyle
        self.interactor_style = MyInteractorStyle()
        self.interactor_style.set_hover_interactor_style(self.hovered_interactor_style)
        self.interactor_style.set_box_picker(self.box_picker)
        self.interactor_style.set_poly_picker(self.poly_picker)
        self.interactor_style.build()

        self.interactor.SetInteractorStyle(self.interactor_style)

        ##################################### Visible Pipeline #####################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import VisiblePipeline
        self.visible_pipeline = VisiblePipeline()
        self.visible_pipeline.set_filter(self.visible_filter)

        ##################################### Hovered Pipeline #####################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import HoveredPipeline
        self.hovered_pipeline = HoveredPipeline()
        self.hovered_pipeline.set_filter(self.hovered_filter)

        ##################################### Picked Pipeline #####################################
        from fem.gui.vtk_widget.vtk_graphics.pipelines import PickedPipeline
        self.picked_pipeline = PickedPipeline()
        self.picked_pipeline.set_filter(self.picked_filter)

        ######################################################################################
        self.visible_pipeline.renderer.SetActiveCamera(self.camera)
        self.visible_pipeline.renderer.ResetCamera()

        self.picked_pipeline.renderer.SetActiveCamera(self.camera)
        self.hovered_pipeline.renderer.SetActiveCamera(self.camera)

        self.interactor_style.SetDefaultRenderer(self.visible_pipeline.renderer)

        self.visible_pipeline.renderer.SetLayer(0)
        self.visible_pipeline.renderer.SetInteractive(1)

        self.picked_pipeline.renderer.SetLayer(1)
        self.picked_pipeline.renderer.SetInteractive(0)

        self.hovered_pipeline.renderer.SetLayer(2)
        self.hovered_pipeline.renderer.SetInteractive(0)

        self.render_window.SetNumberOfLayers(3)
        self.render_window.AddRenderer(self.hovered_pipeline.renderer)
        self.render_window.AddRenderer(self.picked_pipeline.renderer)
        self.render_window.AddRenderer(self.visible_pipeline.renderer)
        self.render_window.SetAlphaBitPlanes(0)

        from fem.gui.vtk_widget.utilities import CoordinateAxes
        self.coordinate_axes = CoordinateAxes(self.interactor)

        self.visible_pipeline.renderer.SetBackground((1, 1, 1))
        self.visible_pipeline.renderer.SetBackground2((0, 0, 1))
        self.visible_pipeline.renderer.GradientBackgroundOn()

        from fem.configuration import config

        from fem.gui.vtk_widget.vtk_graphics.picking import PickingManager
        config.register_picking_manager(PickingManager.instance())

    def _groups_changed(self):
        self.visible_filter.Modified()
        self.render()

    def _key_down(self, key):
        if key == '+':
            self.first_filter.set_size(self.first_filter.size + 1)
        elif key == '-':
            self.first_filter.set_size(self.first_filter.size - 1)

        self.render()

    def set_bdf_data(self, bdf_data):
        self.bdf_data = bdf_data
        self.first_filter.set_bdf_data(bdf_data)

    def set_rotation_center(self, center):
        # noinspection PyBroadException
        try:
            first = center[0]
            if len(center) < 3:
                return
            if not isinstance(first, float):
                center = list(map(float, center))
        except Exception:
            try:
                center = list(map(float, str(center).split(' ')))
                if len(center) < 3:
                    return
            except Exception:
                return

        self.interactor_style.set_center_of_rotation(center)
        # FIXME: update below
        # self.vtk_widget.rotation_sphere.SetCenter(center[0], center[1], center[2])
        self.render()

    def switch_perspective(self):

        if self._perspective == 'perspective':
            self._perspective = 'parallel'
            self.camera.ParallelProjectionOn()
        else:
            self._perspective = 'perspective'
            self.camera.ParallelProjectionOff()

        self.fit_view()

    def ugrid_from_nastran(self, ugrid):
        np_array = dsa.WrapDataObject(ugrid).GetCellData().GetArray("global_ids")
        self.visible_selection.set_data(np_array)
        self.fem_groups.add_group("Default")
        self.fem_groups.get_group('Default').set_data(np_array)

    def set_ugrid(self, ugrid):
        self.data_source.set_input_data(ugrid)
        self.ugrid_from_nastran(ugrid)
        self.fit_view()
        self.render()

    def swap_visible(self):
        self.visible_filter.toggle_visible()
        self.switch_backgrounds()
        self.render()

    def switch_backgrounds(self):
        bg1 = self.visible_pipeline.renderer.GetBackground()
        bg2 = self.visible_pipeline.renderer.GetBackground2()

        self._bg_color_1 = bg2
        self._bg_color_2 = bg1

        self.visible_pipeline.renderer.SetBackground(self._bg_color_1)
        self.visible_pipeline.renderer.SetBackground2(self._bg_color_2)

    def plot_fem(self, data):
        if isinstance(data, str):
            data = FemSelection().set_from_str(data)

        #picked = self.picked_selection
        self.visible_selection.add_data(data.to_set())
        #picked.remove_data(picked.to_set())

        self.visible_filter.Modified()
        self.render()

    def erase_fem(self, data):
        if isinstance(data, str):
            data = FemSelection().set_from_str(data)

        # picked = self.picked_selection
        self.visible_selection.remove_data(data.to_set())
        # picked.remove_data(picked.to_set())

        self.visible_filter.Modified()
        self.render()

    def visible_only(self):
        self.hovered_interactor_style.visible_only()

    def render(self):
        self.interactor.GetRenderWindow().Render()

    def fit_view(self):
        self.visible_pipeline.renderer.ResetCamera()
        self.visible_pipeline.renderer.ResetCameraClippingRange()
        self.render()

    def finalize(self):
        self.render_window.RemoveRenderer(self.hovered_pipeline.renderer)
        self.render_window.RemoveRenderer(self.visible_pipeline.renderer)
        self.render_window.RemoveRenderer(self.picked_pipeline.renderer)

        self.render_window = None

        self.hovered_pipeline.finalize()
        self.visible_pipeline.finalize()
        self.picked_pipeline.finalize()

        self.hovered_pipeline = None
        self.visible_pipeline = None
        self.picked_pipeline = None

        self.interactor_style.finalize()
        self.hovered_interactor_style.finalize()

        self.interactor_style = None
        self.hovered_interactor_style = None

        self.box_picker.finalize()
        self.box_picker = None
        self.poly_picker.finalize()
        self.poly_picker = None

        self.interactor = None

        self.first_filter.finalize()
        self.first_filter = None

        self.data_source = None

        self.__class__._instance = None

        from fem.gui.vtk_widget.vtk_graphics.picking import PickingManager
        picking_manager = PickingManager.instance()
        picking_manager.finalize()

    def serialize(self):
        data = {
            'camera': self.serialize_camera_data()
        }

        return data

    def load(self, data):
        try:
            _data = data['camera']

            self.load_camera_data(_data, True)

        except KeyError:
            pass

    def serialize_camera_data(self):
        data = {
            'position': list(self.camera.GetPosition()),
            'focal_point': list(self.camera.GetFocalPoint()),
            'view_angle': self.camera.GetViewAngle(),
            'view_up': list(self.camera.GetViewUp()),
            'view_plane_normal': list(self.camera.GetViewPlaneNormal()),
            'distance': self.camera.GetDistance()
        }

        return data

    def load_camera_data(self, data, render=False):
        self.camera.SetFocalPoint(data['focal_point'])
        self.camera.SetViewAngle(data['view_angle'])
        self.camera.SetViewUp(data['view_up'])
        self.camera.SetPosition(data['position'])
        self.camera.SetDistance(data['distance'])
        # self.camera.SetViewPlaneNormal(_data['view_plane_normal'])

        if render is True:
            self.visible_pipeline.renderer.ResetCameraClippingRange()
            self.render()


# VTKGraphics = _VTKGraphics.register(_VTKGraphics)
# """:type: _VTKGraphics"""
