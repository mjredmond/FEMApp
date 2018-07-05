from __future__ import print_function, absolute_import

from qtpy import QtWidgets


class VTKWidget(QtWidgets.QWidget):
    def __init__(self, main_window):
        super(VTKWidget, self).__init__(main_window)

        self.main_window = main_window
        """:type: gui.main_window.main_window.MainWindow"""

        self.main_window.setCentralWidget(self)

        self.interactor = None
        """:type: gui.vtk_widget.utilities.MyQVTKRenderWindowInteractor"""

        self.setLayout(QtWidgets.QGridLayout())
        # self.layout().addWidget(self.interactor)

        self.render_window = None
        """:type: vtk.vtkRenderWindow"""
        self.iren = None
        """:type: vtk.vtkRenderWindowInteractor"""

        self.vtk_graphics = None
        """:type: gui.vtk_widget.vtk_graphics.VTKGraphics"""

        self.graphics_toolbar = None
        """:type: gui.vtk_widget.graphics_toolbar.GraphicsToolBar"""

        self.picking_toolbar = None
        """:type: gui.vtk_widget.picking_toolbar.PickingToolbar"""

        self.plotting_toolbar = None
        """:type: gui.vtk_widget.plotting_toolbar.PlottingToolbar"""

        self.groups_toolbar = None
        """:type: gui.vtk_widget.groups_toolbar.GroupsToolbar"""

    def initialize(self):
        from .utilities import MyQVTKRenderWindowInteractor
        self.interactor = MyQVTKRenderWindowInteractor(self)
        self.layout().addWidget(self.interactor)

        self.render_window = self.interactor.GetRenderWindow()
        self.iren = self.render_window.GetInteractor()

        from .vtk_graphics import VTKGraphics
        self.vtk_graphics = VTKGraphics(self)
        self.vtk_graphics.build()
        self.iren.Initialize()

        from .graphics_toolbar import GraphicsToolbar
        self.graphics_toolbar = GraphicsToolbar(self.main_window)
        self.main_window.addToolBar(self.graphics_toolbar)

        from .picking_toolbar import PickingToolbar
        self.picking_toolbar = PickingToolbar(self.main_window)
        self.main_window.addToolBar(self.picking_toolbar)

        from .plotting_toolbar import PlottingToolbar
        self.plotting_toolbar = PlottingToolbar(self.main_window)
        self.main_window.addToolBar(self.plotting_toolbar)

        from .groups_toolbar import GroupsToolbar
        self.groups_toolbar = GroupsToolbar(self.main_window)
        self.main_window.addToolBar(self.groups_toolbar)

    def finalize(self):
        self.vtk_graphics.finalize()
        self.vtk_graphics = None

        self.layout().removeWidget(self.interactor)
        self.interactor.Finalize()  # might be unnecessary now
        self.interactor.setParent(None)
        self.interactor = None

        self.render_window = None
        self.iren = None

        self.main_window.setCentralWidget(None)
        self.setParent(None)

        self.main_window.removeToolBar(self.graphics_toolbar)
        self.graphics_toolbar.setParent(None)
        self.graphics_toolbar = None

        self.main_window.removeToolBar(self.picking_toolbar)
        self.picking_toolbar.setParent(None)
        self.picking_toolbar = None

        self.main_window.removeToolBar(self.plotting_toolbar)
        self.plotting_toolbar.setParent(None)
        self.plotting_toolbar = None

        self.main_window.removeToolBar(self.groups_toolbar)
        self.groups_toolbar.setParent(None)
        self.groups_toolbar = None
