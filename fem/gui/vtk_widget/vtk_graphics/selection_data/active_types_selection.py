from __future__ import print_function, absolute_import

from fem.model.bdf.card_info_list import CardInfoList
from fem.utilities.debug import debuginfo
from .fem_selection import FemSelection

bdf_card_info = CardInfoList.instance()
""":type: CardInfoList"""

from six.moves import range


class ActiveTypesSelection(FemSelection):
    def __init__(self):
        super(ActiveTypesSelection, self).__init__()

    def add_all(self):
        self.add_data([i for i in range(1000)])

    def remove_all(self):
        self.clear()

    def add_all_fem(self):
        self.add_data(list(bdf_card_info.all_fem()))

    def remove_all_fem(self):
        self.remove_data(list(bdf_card_info.all_fem()))

    def add_all_point_fem(self):
        self.add_data(list(bdf_card_info.point_fem()))

    def remove_all_point_fem(self):
        self.remove_data(list(bdf_card_info.point_fem()))

    def add_all_line_fem(self):
        self.add_data(list(bdf_card_info.line_fem()))

    def remove_all_line_fem(self):
        self.remove_data(list(bdf_card_info.line_fem()))

    def add_all_shell_fem(self):
        self.add_data(list(bdf_card_info.shell_fem()))

    def remove_all_shell_fem(self):
        self.remove_data(list(bdf_card_info.shell_fem()))

    def add_all_solid_fem(self):
        self.add_data(list(bdf_card_info.solid_fem()))

    def remove_all_solid_fem(self):
        self.remove_data(list(bdf_card_info.solid_fem()))

    def add_all_tri_fem(self):
        self.add_data(list(bdf_card_info.tri_fem()))

    def remove_all_tri_fem(self):
        self.remove_data(list(bdf_card_info.tri_fem()))

    def add_all_quad_fem(self):
        self.add_data(list(bdf_card_info.quad_fem()))

    def remove_all_quad_fem(self):
        self.remove_data(list(bdf_card_info.quad_fem()))

    def add_all_grid_fem(self):
        self.add_data(list(bdf_card_info.grid_fem()))

    def remove_all_grid_fem(self):
        self.remove_data(list(bdf_card_info.grid_fem()))

    def add_all_mpc_fem(self):
        self.add_data(list(bdf_card_info.mpc_fem()))

    def remove_all_mpc_fem(self):
        self.remove_data(list(bdf_card_info.mpc_fem()))

    def add_all_coord_fem(self):
        self.add_data(list(bdf_card_info.coord_fem()))

    def remove_all_coord_fem(self):
        self.remove_data(list(bdf_card_info.coord_fem()))
