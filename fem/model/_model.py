from __future__ import print_function, absolute_import

import ast
import json
import tarfile
from h5Nastran import H5Nastran

from fem.utilities.debug import debuginfo
from fem.configuration import config

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO


class Model(object):
    def __init__(self):
        super(Model, self).__init__()

        self._model_name = ''
        self.h5n = None  # type: H5Nastran
        self.ugrid = None

        # self.collector = Collector()
        
    def import_bdf(self, filename):
        h5filename = filename.replace('.bdf', '.h5')
        self.h5n = H5Nastran(h5filename, 'w', in_memory=True)
        self.h5n.load_bdf(filename)

        # TODO: vtk data should be stored in model
        # it's all kind of a mess right now
        from .bdf.ugrid import UGrid
        self.ugrid = UGrid.make_from_bdf(self.h5n.bdf)

        from .bdf.ugrid_from_nastran import ugrid_from_nastran
        ugrid_from_nastran(self.ugrid)

    def set_model_name(self, model_name):
        self._model_name = model_name

    def model_name(self):
        return self._model_name

    def set_data(self, data):
        from fem.gui.vtk_widget.vtk_graphics import VTKGraphics
        vtk_graphics = VTKGraphics.instance()
        fem_groups = vtk_graphics.fem_groups

        self.clear()

        # FIXME: shouldn't be done this way
        config.main_window().file_menu.import_model(data['model_name'])
        fem_groups.load(data['groups'])

        try:
            vtk_graphics.load(data['graphics'])
        except KeyError:
            pass

        from fem.gui import MainWindow
        mw = MainWindow.instance()
        """:type: fem.gui.MainWindow"""

        mw.plugins.load_data(data['plugins'])

    def serialize(self):
        from fem.gui.vtk_widget.vtk_graphics import VTKGraphics
        vtk_graphics = VTKGraphics.instance()
        fem_groups = vtk_graphics.fem_groups

        data = {}

        data['application'] = config.application_info()
        data['model_name'] = self._model_name
        data['groups'] = fem_groups.serialize()
        data['graphics'] = vtk_graphics.serialize()

        from fem.gui import MainWindow
        mw = MainWindow.instance()
        """:type: fem.gui.MainWindow"""

        data['plugins'] = mw.plugins.serialize()

        return data

    def tostring(self):
        return str(self.serialize())

    def tojson(self):
        return json.loads(self.serialize())

    def clear(self):
        self._model_name = ''

        from fem.gui.vtk_widget.vtk_graphics import VTKGraphics
        vtk_graphics = VTKGraphics.instance()
        fem_groups = vtk_graphics.fem_groups

        fem_groups.clear()

    def read_from_file(self, filename):
        data = {}

        def read_data(member):
            tmp = tar.extractfile(member).read().decode('utf-8')
            try:
                return ast.literal_eval(tmp)
            except Exception:
                return tmp

        tar = tarfile.open(filename, 'r:gz')

        data['model_name'] = read_data('model')
        data['groups'] = read_data('groups')
        data['graphics'] = read_data('graphics')
        data['plugins'] = read_data('plugins')

        tar.close()

        return data

    def save_to_file(self, filename):
        tar = tarfile.open(filename, 'w:gz')

        def add_data(info_name, data):
            data = data.encode('utf-8')
            info = tarfile.TarInfo(info_name)
            info.size = len(data)
            tar.addfile(info, StringIO(data))

        from fem.gui.vtk_widget.vtk_graphics import VTKGraphics
        vtk_graphics = VTKGraphics.instance()
        fem_groups = vtk_graphics.fem_groups

        debuginfo(1)

        # try:
        add_data(
            'application',
            str(config.application_info())
        )

        debuginfo(2)

        add_data(
            'model',
            self._model_name
        )

        debuginfo(3)

        add_data(
            'groups',
            str(fem_groups.serialize())
        )

        debuginfo(4)

        add_data(
            'graphics',
            str(vtk_graphics.serialize())
        )

        debuginfo(5)

        from fem.gui import MainWindow
        mw = MainWindow.instance()
        """:type: fem.gui.MainWindow"""

        debuginfo(6)

        print(mw.plugins.serialize())

        debuginfo(7)

        add_data(
            'plugins',
            str(mw.plugins.serialize())
        )

        debuginfo(8)

        # finally:
        tar.close()

        debuginfo(9)
