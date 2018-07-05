from __future__ import print_function, absolute_import

from qtpy import QtGui, QtCore, QtWidgets

from ..gui_helper import GUIPath
from ..vtk_graphics import VTKGraphics
from ..vtk_graphics.picking import PickingManager

gui_path = GUIPath("picking_toolbar/images")

vtk_graphics = VTKGraphics.instance()

picking_manager = PickingManager.instance()


class PickingToolbar(QtWidgets.QToolBar):
    def __init__(self, parent):
        super(PickingToolbar, self).__init__(parent)

        self.visible_only_action = self._add_action(QtGui.QIcon(gui_path("visible_only.png")),
                                                    "&Visible Only", self,
                                                    statusTip="Select visible elements only",
                                                    triggered=self.visible_only)

        self.addSeparator()

        self.box_picking_action = self._add_action(QtGui.QIcon(gui_path("box_picking.png")),
                                                   "&Box Picking", self,
                                                   statusTip="Select by box picking",
                                                   triggered=self.box_picking)

        self.poly_picking_action = self._add_action(QtGui.QIcon(gui_path("poly_picking.png")),
                                                    "&Poly Picking", self,
                                                    statusTip="Select by poly picking",
                                                    triggered=self.poly_picking)

        self.addSeparator()

        self.append_selection_action = self._add_action(QtGui.QIcon(gui_path("append_selection.png")),
                                                        "&Append Selection", self,
                                                        statusTip="Append to current selection",
                                                        triggered=self.append_selection)

        self.subtract_selection_action = self._add_action(QtGui.QIcon(gui_path("subtract_selection.png")),
                                                          "&Subtract Selection", self,
                                                          statusTip="Subtract from current selection",
                                                          triggered=self.subtract_selection)

        self.set_selection_action = self._add_action(QtGui.QIcon(gui_path("set_selection.png")),
                                                     "&Set Selection", self,
                                                     statusTip="Set current selection",
                                                     triggered=self.set_selection)

        self.addSeparator()

        self.select_all_fem_action = self._add_action(QtGui.QIcon(gui_path("select_all_fem.png")),
                                                   "&Select Any", self,
                                                   statusTip="Select any",
                                                   triggered=self.select_all_fem)

        self.select_node_action = self._add_action(QtGui.QIcon(gui_path("select_node.png")),
                                                   "&Select Nodes", self,
                                                   statusTip="Select only nodes",
                                                   triggered=self.select_node)

        self.select_all_elements_action = self._add_action(QtGui.QIcon(gui_path("select_all_elements.png")),
                                                  "&Select All Elements", self,
                                                  statusTip="Select all element types",
                                                  triggered=self.select_all_elements)

        self.select_point_action = self._add_action(QtGui.QIcon(gui_path("select_point_element.png")),
                                                    "&Select Point Elements", self,
                                                    statusTip="Select point elements",
                                                    triggered=self.select_point)

        self.select_line_action = self._add_action(QtGui.QIcon(gui_path("select_line_element.png")),
                                                   "&Select Line Elements", self,
                                                   statusTip="Select line elements",
                                                   triggered=self.select_line)

        self.select_tri_action = self._add_action(QtGui.QIcon(gui_path("select_tri_element.png")),
                                                  "&Select Triangle Elements", self,
                                                  statusTip="Select triangle elements",
                                                  triggered=self.select_tri)

        self.select_quad_action = self._add_action(QtGui.QIcon(gui_path("select_quad_element.png")),
                                                   "&Select Quad Elements", self,
                                                   statusTip="Select quad elements",
                                                   triggered=self.select_quad)

        self.select_shell_action = self._add_action(QtGui.QIcon(gui_path("select_shell_element.png")),
                                                    "&Select Shell Elements", self,
                                                    statusTip="Select shell elements",
                                                    triggered=self.select_shell)

        #self.select_tet_action = self._add_action("&Select Tet Elements", self,
        #                                          statusTip="Select tet elements",
        #                                          triggered=self.select_tet)

        #self.select_wedge_action = self._add_action("&Select Wedge Elements", self,
        #                                            statusTip="Select wedge elements",
        #                                            triggered=self.select_wedge)

        #self.select_solid_action = self._add_action("&Select Solid Elements", self,
        #                                            statusTip="Select solid elements",
        #                                            triggered=self.select_solid)

        self.select_free_edge_action = self._add_action(QtGui.QIcon(gui_path("select_free_edges.png")),
                                                        "&Select Elements with Free Edges", self,
                                                        statusTip="Select elements with free edges",
                                                        triggered=self.select_free_edge)

        #self.select_free_face_action = self._add_action("&Select w/Free Faces", self,
        #                                                statusTip="Select elements with free faces",
        #                                                triggered=self.select_free_face)

        self.select_mpc_action = self._add_action(QtGui.QIcon(gui_path("select_mpcs.png")),
                                                  "&Select MPC's", self,
                                                  statusTip="Select MPC's",
                                                  triggered=self.select_mpc)

        self.select_all_fem_action.setChecked(True)

        self._pass = False

        picking_manager.picking_finished.connect(self._picking_done)

        #selection_data.box_picker_done.connect(self.box_picker_done)
        #selection_data.poly_picker_done.connect(self.poly_picker_done)

        self.setIconSize(QtCore.QSize(16, 16))

    def _add_action(self, *args, **kwargs):
        action = QtWidgets.QAction(*args, **kwargs)
        action.setCheckable(True)
        self.addAction(action)
        return action

    def visible_only(self):
        if self.box_picking_action.isChecked() or self.poly_picking_action.isChecked():
            self.visible_only_action.setChecked(False)
            return

        vtk_graphics.visible_only()

    def box_picking(self):
        self.visible_only()
        self.visible_only_action.setChecked(False)
        self.poly_picking_action.setChecked(False)
        picking_manager.box_picker_activate()

    def _picking_done(self):
        self.box_picking_action.setChecked(False)
        self.poly_picking_action.setChecked(False)

    def poly_picking(self):
        self.visible_only()
        self.visible_only_action.setChecked(False)
        self.box_picking_action.setChecked(False)
        picking_manager.poly_picker_activate()

    def set_selection(self):
        self.append_selection_action.setChecked(False)
        self.subtract_selection_action.setChecked(False)
        picking_manager.set_picking_option(1)
        self._check_selections(self.set_selection, self.set_selection_action)

    def append_selection(self):
        self.set_selection_action.setChecked(False)
        self.subtract_selection_action.setChecked(False)
        picking_manager.set_picking_option(2)
        self._check_selections(self.append_selection, self.append_selection_action)

    def subtract_selection(self):
        self.set_selection_action.setChecked(False)
        self.append_selection_action.setChecked(False)
        picking_manager.set_picking_option(3)
        self._check_selections(self.subtract_selection, self.subtract_selection_action)

    def _check_selections(self, method, action):
        if self._pass:
            return

        if not self.set_selection_action.isChecked() and \
                not self.append_selection_action.isChecked() and \
                not self.subtract_selection_action.isChecked():
            self._pass = True
            method()
            self._pass = False
            action.setChecked(True)

    def _deselect_all(self):
        self.select_all_fem_action.setChecked(False)
        self.select_node_action.setChecked(False)
        self.select_all_elements_action.setChecked(False)
        self.select_point_action.setChecked(False)
        self.select_line_action.setChecked(False)
        self.select_tri_action.setChecked(False)
        self.select_quad_action.setChecked(False)
        self.select_shell_action.setChecked(False)
        self.select_free_edge_action.setChecked(False)
        self.select_mpc_action.setChecked(False)

    def select_all_fem(self):
        self._deselect_all()
        self.select_all_fem_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all_fem()
        vtk_graphics.pickable_types.add_all_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def select_node(self):
        self._deselect_all()
        self.select_node_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all_grid_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def select_all_elements(self):
        self._deselect_all()
        self.select_all_elements_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all()
        vtk_graphics.pickable_types.remove_all_grid_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def select_point(self):
        self._deselect_all()
        self.select_point_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all_point_fem()
        vtk_graphics.pickable_types.data_changed.unblock()

    def select_line(self):
        self._deselect_all()
        self.select_line_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all_line_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def select_tri(self):
        self._deselect_all()
        self.select_tri_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all_tri_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def select_quad(self):
        self._deselect_all()
        self.select_quad_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all_quad_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def select_shell(self):
        self._deselect_all()
        self.select_shell_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all_shell_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def select_tet(self):
        pass

    def select_wedge(self):
        pass

    def select_solid(self):
        pass

    def select_free_edge(self):
        self._deselect_all()
        self.select_free_edge_action.setChecked(True)

    def select_free_face(self):
        pass

    def select_mpc(self):
        self._deselect_all()
        self.select_mpc_action.setChecked(True)

        vtk_graphics.pickable_types.data_changed.block()
        vtk_graphics.pickable_types.remove_all()
        vtk_graphics.pickable_types.add_all_mpc_fem()
        vtk_graphics.pickable_types.data_changed.unblock()
        self._data_changed()

    def _data_changed(self):
        vtk_graphics.pickable_filter.Modified()
        vtk_graphics.pickable_filter.Update()
        vtk_graphics.pickable_types.data_changed.emit()
