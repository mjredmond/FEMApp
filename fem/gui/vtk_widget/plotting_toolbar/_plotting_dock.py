from __future__ import print_function, absolute_import

from qtpy import QtWidgets

from ._plotting_ui import Ui_DockWidget
from ..vtk_graphics import VTKGraphics
from ..vtk_graphics.pipelines.picked import PickedSelection

vtk_graphics = VTKGraphics.instance()


class PlainTextEditDelegate(object):
    def __init__(self, parent, dock_widget):
        self.parent = parent
        """:type: QtGui.QPlainTextEdit"""

        self.dock_widget = dock_widget
        """:type: PlottingDock"""

        self.delegate = QtWidgets.QPlainTextEdit()

        self.parent.enterEvent = self.enter_event
        self.parent.leaveEvent = self.leave_event

    def enter_event(self, *args):
        picked_selection = vtk_graphics.picked_selection
        picked_selection.data_changed.block()
        picked_selection.set_from_str(str(self.parent.toPlainText()))
        picked_selection.data_changed.unblock()
        vtk_graphics.visible_filter.Modified()

        # sometimes an exception occurs with closing the app, because the interactor has been set to None already
        try:
            vtk_graphics.render()
        except AttributeError:
            pass

    def leave_event(self, *args):
        picked_selection = vtk_graphics.picked_selection
        picked_selection.data_changed.block()
        picked_selection.set_from_str(str(self.parent.toPlainText()))
        picked_selection.data_changed.unblock()
        vtk_graphics.visible_filter.Modified()

        # sometimes an exception occurs with closing the app, because the interactor has been set to None already
        try:
            vtk_graphics.render()
        except AttributeError:
            pass


class PlottingDock(QtWidgets.QDockWidget):
    def __init__(self, main_window):
        super(PlottingDock, self).__init__(main_window)

        self.main_window = main_window

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.plot_button.clicked.connect(self._plot)
        self.ui.erase_button.clicked.connect(self._erase)
        self.ui.done_button.clicked.connect(self._done)

        self.ui.plainTextEdit.textChanged.connect(self._text_changed)

        self.ui.plainTextEdit.setReadOnly(False)

        self.ui.listWidget.itemChanged.connect(self._item_changed)

        self.delegate = PlainTextEditDelegate(self.ui.plainTextEdit, self)

        self.setWindowTitle('Hide/Show FEM')

        self._selection = PickedSelection()

        self._selection.data_changed.connect(self._picked_data_changed)

    def show_and_register(self):
        self.show()

        # from fem.gui.vtk_widget.vtk_graphics import VTKGraphics
        # vtk_graphics = VTKGraphics.instance()
        # vtk_graphics.picked_selection.data_changed.disconnect_all()
        # vtk_graphics.picked_selection.data_changed.connect(self._picked_data_changed)

        from ..vtk_graphics.picking import PickingManager

        picking_manager = PickingManager.instance()
        picking_manager.register_selection(self._selection)

        self.main_window.show_dock(self)

    def build(self, vtk_config):
        # self.vtk_config = vtk_config
        """:type: vtk_fem.vtk_widget.vtk_widget.vtk_config.VTKConfig"""
        # self.vtk_config.picked_selection.data_changed.connect(self._picked_data_changed)
        pass

    def _plot(self):
        vtk_graphics.plot_fem(str(self.ui.plainTextEdit.toPlainText()))

    def _erase(self):
        vtk_graphics.erase_fem(str(self.ui.plainTextEdit.toPlainText()))

    def _done(self):
        self.hide()

    def closeEvent(self, QCloseEvent):
        super(PlottingDock, self).closeEvent(QCloseEvent)

    def _picked_data_changed(self, *args):
        self.ui.plainTextEdit.blockSignals(True)
        self.ui.plainTextEdit.setPlainText(self._selection.to_str())
        self.ui.plainTextEdit.blockSignals(False)

    def _text_changed(self, *args, **kwargs):
        print(args, kwargs)

    def _item_changed(self, item):
        item_txt = item.text()
        item_state = item.checkState()

        if item_txt == "All":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all()
            else:
                vtk_graphics.visible_types.add_all()

        elif item_txt == "FEM":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_fem()
            else:
                vtk_graphics.visible_types.add_all_fem()

        elif item_txt == "Grid":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_grid_fem()
            else:
                vtk_graphics.visible_types.add_all_grid_fem()

        elif item_txt == "Point Elements":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_point_fem()
            else:
                vtk_graphics.visible_types.add_all_point_fem()

        elif item_txt == "Line Elements":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_line_fem()
            else:
                vtk_graphics.visible_types.add_all_line_fem()

        elif item_txt == "Tri Elements":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_tri_fem()
            else:
                vtk_graphics.visible_types.add_all_tri_fem()

        elif item_txt == "Quad Elements":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_quad_fem()
            else:
                vtk_graphics.visible_types.add_all_quad_fem()

        elif item_txt == "Shell Elements":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_shell_fem()
            else:
                vtk_graphics.visible_types.add_all_shell_fem()

        elif item_txt == "MPC's":
            if item_state == 0:
                vtk_graphics.visible_types.remove_all_mpc_fem()
            else:
                vtk_graphics.visible_types.add_all_mpc_fem()

        vtk_graphics.visible_filter.Modified()
        vtk_graphics.render()

    def enterEvent(self, *args, **kwargs):
        print('enter')

    def leaveEvent(self, *args, **kwargs):
        print('leave')
