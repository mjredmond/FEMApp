from __future__ import print_function, absolute_import

import os

from fem import app_path


def gui_path(path):
    return os.path.join(app_path, path)


class GUIPath(object):
    def __init__(self, folder):
        self.gui_folder = app_path + '/gui/vtk_widget/' + folder

    def __call__(self, filename):
        return os.path.join(self.gui_folder, filename)