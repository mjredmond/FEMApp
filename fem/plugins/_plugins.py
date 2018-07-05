from __future__ import print_function, absolute_import

from ..configuration import config


# import grid_point_force

# FIXME: the Plugins class needs to be agnostic to ALL plugins


# noinspection PyPep8Naming
class Plugins(object):
    def __init__(self, main_window):
        super(Plugins, self).__init__()

        self.main_window = main_window
        """:type: fem.gui.MainWindow"""

        # self.gpf = grid_point_force.get_plugin()(self.main_window, config)

        # FIXME: accessing private member
        # self.main_window._current_dock = self.gpf.dock

    def load_collector(self, collector):
        # self.gpf.load_collector(collector)
        pass

    def load_database(self, filename):
        # self.gpf.load_database(filename)
        pass

    def bdf_data(self, index):
        # return self.gpf.bdf_data(index)
        return None

    def finalize(self):
        # self.gpf.finalize()
        pass

    def serialize(self):
        # return {
        #     'grid_point_force': self.gpf.serialize()
        # }
        return {}

    def load_data(self, data):
        # self.gpf.load_data(data['grid_point_force'])
        pass

