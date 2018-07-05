from __future__ import print_function, absolute_import

from qtpy import QtWidgets

from fem.utilities.qtfile import getopenfilename
from ...configuration import config
from ...plugins import Plugins


class FileMenu(object):
    def __init__(self, main_window):
        self.main_window = main_window

        self.menu_bar = self.main_window.menuBar()
        """:type: QtWidgets.QMenuBar"""

        self.file_menu = self.menu_bar.addMenu("&File")
        """:type: QtWidgets.QMenu"""

        self.actionOpen = self.file_menu.addAction('Open...')
        self.actionOpen.setShortcut('Ctrl+O')

        self.separator_1 = self.file_menu.addSeparator()

        self.actionSave = self.file_menu.addAction('Save')
        self.actionSave.setShortcut('Ctrl+S')

        self.actionSaveAs = self.file_menu.addAction('Save As...')
        self.actionSaveAs.setShortcut('Ctrl+Shift+S')

        self.separator_2 = self.file_menu.addSeparator()

        self.actionSaveMacro = self.file_menu.addAction('Save Macro...')
        self.actionSaveMacro.setShortcut('Ctrl+M')

        self.actionRunMacro = self.file_menu.addAction('Run Macro...')
        self.actionRunMacro.setShortcut('Ctrl+Shift+M')

        self.separator_3 = self.file_menu.addSeparator()

        self.actionClose = self.file_menu.addAction('Close')
        self.actionClose.setShortcut('Ctrl+Shift+C')

        self.separator_4 = self.file_menu.addSeparator()

        self.actionQuit = self.file_menu.addAction('Quit')
        self.actionQuit.setShortcut('Ctrl+Q')

        self.actionOpen.triggered.connect(self._open)
        self.actionSave.triggered.connect(self._save)
        self.actionSaveAs.triggered.connect(self.save_as)
        self.actionClose.triggered.connect(self._close)
        self.actionQuit.triggered.connect(self._quit)

        self.actionSaveMacro.triggered.connect(self._save_macro)
        self.actionRunMacro.triggered.connect(self._run_macro)

        self.config = config
        self.dispatch = self.config.dispatcher.dispatch

        self.actionImport = QtWidgets.QAction('Import BDF...', self.file_menu)
        self.file_menu.insertAction(self.separator_1, self.actionImport)

        self.actionImport.triggered.connect(self.import_model)

    def import_model_new(self, filename=None):

        plugins = Plugins.instance()

        # FIXME: needs to be done by an action

        if filename is None or filename == '' or filename is False:
            filename = getopenfilename(
                caption='Import Punch Binary File',
                directory=config.directory(),
                filter_=r'.pbf File (*.pbf)'
            )

        if filename in ('', None):
            return

        from fem.model import Model
        main_data = Model.instance()
        """:type: fem.model.MainData"""

        main_data.collector.set_filename(filename)

        plugins.load_collector(main_data.collector)

        bdf_data = main_data.collector.readers[0].header_data.get_bdf_data()

        from mrNastran import BdfData

        # bdf_data = BdfData()
        # with open(filename, 'rb') as f:
        #     buffer_ = f.read()
        #     bdf_data.read_from_buffer(buffer_, len(buffer_))

        ugrid = BdfData.to_vtk(bdf_data)

        # ugrid = bdf_data.to_vtk()

        # from fem.gui.vtk_widget.vtk_graphics import VTKGraphics
        vtk_graphics = self.main_window.vtk_widget.vtk_graphics
        vtk_graphics.set_ugrid(ugrid)
        vtk_graphics.set_bdf_data(bdf_data)

        from fem.model._model import Model
        main_data = Model.instance()

        main_data.set_model_name(filename)

    def import_model(self, filename=None):
        # FIXME: needs to be done by an action

        if filename is None or filename == '' or filename is False:
            filename = getopenfilename(
                caption='Import BDF Model',
                directory=config.directory(),
                filter_=r'BDF File (*.bdf)'
            )

        if filename in ('', None):
            return

        model = self.main_window.get_model()

        model.import_bdf(filename)

        h5n = model.h5n
        ugrid = model.ugrid

        # from fem.gui.vtk_widget.vtk_graphics import VTKGraphics
        vtk_graphics = self.main_window.vtk_widget.vtk_graphics
        vtk_graphics.set_ugrid(ugrid)
        vtk_graphics.set_bdf_data(None)

        model.set_model_name(filename)

    def _open(self, filename=None):
        if filename is None or filename == '' or filename is False:
            config = self.config
            filename = getopenfilename(
                'Open %s File' % config.application_name(),
                config.directory(),
                r'%s File (*.%s)' % (config.application_name(), config.file_extension())
            )

        if filename in ('', None):
            return

        self.dispatch(('File.read', (filename,)))

    def _save(self, filename=None):
        if filename is None or filename == '' or filename is False:
            filename = self.config.filename()

        if filename is None or filename == '' or filename is False:
            return self.save_as()

        self.dispatch(('File.save', (filename,)))

    def save_as(self):
        config = self.config
        filename = getsavefilename(
            'Save %s File' % config.application_name(),
            config.directory(),
            r'%s File (*.%s)' % (config.application_name(), config.file_extension())
        )

        if filename in ('', None):
            return

        self._save(filename)

        return True

    def _close(self):
        if not self.check_on_close():
            return

        self.dispatch(('File.close', tuple([self.config.filename(),])))

    def _save_macro(self, *args):
        config = self.config
        filename = getsavefilename(
            'Save %s File' % config.macro_extension().upper(),
            config.directory(),
            r'%s Macro File (*.%s)' % (config.application_name(), config.macro_extension())
        )

        if filename in ('', None):
            return

        with open(filename, 'w') as f:

            info = config.application_info()

            f.write('# %s\n' % info['Application Name'])
            f.write('# %s\n' % info['Application Version'])
            f.write('# %s\n' % info['Date'])
            f.write('# %s\n' % info['Time'])
            f.write('# %s\n' % info['User ID'])

            f.write(self.main_window.logging_dock.log_text())

    def _run_macro(self, *args):
        config = self.config
        filename = getopenfilename(
            'Open %s File' % 'Open %s File' % config.macro_extension().upper(),
            config.directory(),
            r'%s Macro File (*.%s)' % (config.application_name(), config.macro_extension())
        )

        if filename in ('', None):
            return

        with open(filename, 'r') as f:
            data = f.read().split('\n')

        for data_ in data:
            if data_[0] == '#':
                continue

            data_ = data_[22:]

            if data_.startswith('Error') or data_.startswith('Info'):
                continue

            try:
                index = data_.index('(')
            except IndexError:
                continue

            command = data_[:index]
            command_data = literal_eval(data_[index:])

            print(command, command_data)

            self.dispatch((command, command_data))

    def _quit(self):
        self.main_window.close()

    def check_on_close(self):
        if not self.config.dispatcher.undo_stack.isClean():
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle('Save Changes?')
            msg_box.setText('Do you want to save changes before closing?')
            msg_box.setStandardButtons(
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
            )
            msg_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
            reply = msg_box.exec_()

            if reply == QtWidgets.QMessageBox.Cancel:
                return False

            if reply == QtWidgets.QMessageBox.Yes:
                if not self.save_as():
                    return False

        return True
