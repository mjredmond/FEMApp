from __future__ import print_function, absolute_import

from fem.utilities import MrSignal
from .single_picker import SinglePicker


class DefaultSinglePicker(SinglePicker):
    def __init__(self, picking_manager):
        super(DefaultSinglePicker, self).__init__()

        self.picking_manager = picking_manager
        """:type: PickingManager"""

    def pick(self, screen_pos, cell_pos, picked_global_id):
        if picked_global_id > 0:
            self.picking_manager.set_picked_data(picked_global_id)
        else:
            self.picking_manager.set_picked_data([])

        self.done.emit()

    def finalize(self):
        super(DefaultSinglePicker, self).finalize()
        self.picking_manager = None


class PickingManager(object):

    _instance = None

    @classmethod
    def instance(cls):
        """

        :return:
        :rtype: PickingManager
        """
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PickingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):

        from fem.gui.vtk_widget.vtk_graphics import VTKGraphics

        self.vtk_graphics = VTKGraphics.instance()
        """:type: fem.gui.vtk_widget.vtk_graphics.VTKGraphics"""

        self.picked_selection = self.vtk_graphics.picked_selection
        """:type: fem.gui.vtk_widget.vtk_graphics.picked.PickedSelection"""

        self.default_single_picker = DefaultSinglePicker(self)
        self._single_pickers = [self.default_single_picker]
        """:type: list[SinglePicker]"""

        self.single_picker = self.default_single_picker

        self.picking_option = 1

        self._registered_selection = None
        """:type: fem.gui.vtk_widget.vtk_graphics.picked.PickedSelection"""

        self.picking_finished = MrSignal()

    def picking_done(self):
        self.picking_finished.emit()

    def register_selection(self, selection):
        if selection is None:
            self._registered_selection = None
            self.picked_selection.data_changed.disconnect_all()
            return

        self._registered_selection = selection

        self.picked_selection.data_changed.block()
        self.picked_selection.copy(self._registered_selection)
        self.picked_selection.data_changed.unblock()

        self.picked_selection.data_changed.disconnect_all()
        self.picked_selection.data_changed.connect(self._picked_selection_changed)

    def register_single_picker(self, single_picker):
        if single_picker is not self.single_picker:
            if self.single_picker is not None:
                try:
                    last_ = self._single_pickers[-1]
                except IndexError:
                    last_ = None
                if self.single_picker is not last_:
                    self._single_pickers.append(self.single_picker)

        self.single_picker = single_picker

    def unload_single_picker(self, picker):
        if picker is self.single_picker:
            try:
                self.single_picker = self._single_pickers.pop()
            except IndexError:
                self.single_picker = None

    def single_pick(self, screen_pos, cell_pos, picked_global_id):
        if self.single_picker is None:
            return

        self.single_picker.pick(screen_pos, cell_pos, picked_global_id)

    def set_picking_option(self, option):
        assert option in (1, 2, 3)

        self.picking_option = option

    def set_picked_data(self, data):
        option = self.picking_option

        if option == 1:
            self.picked_selection.set_data(data)
        elif option == 2:
            self.picked_selection.add_data(data)
        elif option == 3:
            self.picked_selection.remove_data(data)
        else:
            raise ValueError

        self.vtk_graphics.picked_filter.Modified()
        self.vtk_graphics.render()

    def box_picker_activate(self):
        self.vtk_graphics.interactor_style.box_picker_activate()

    def poly_picker_activate(self):
        self.vtk_graphics.interactor_style.poly_picker_activate()

    def _picked_selection_changed(self, *args):
        if self._registered_selection is None:
            return

        self._registered_selection.copy(self.picked_selection)

    def finalize(self):
        for picker in self._single_pickers:
            picker.finalize()

        del self._single_pickers[:]

        self.default_single_picker.finalize()
        self.default_single_picker = None

        self.vtk_graphics = None
