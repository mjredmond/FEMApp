from __future__ import print_function, absolute_import

import datetime
import getpass
import json
import os
from collections import OrderedDict
from qtpy import QtWidgets, QtGui

from fem.utilities import MrSignal, BaseObject
from fem.utilities.command_dispatcher import CommandDispatcher
from ..config_file import config_file


class Configuration(object):
    config_file = config_file
    _major_version = 0
    _minor_version = 0
    _micro_version = 0
    _other_version = 'alpha'

    def __init__(self):
        self._database_exe = None

        self._application_name = 'N/A'

        self._user_manual = None
        self._email_recipient = None

        self._long_name = None
        self._date_created = None
        self._date_modified = None
        self._author = None
        self._description = None

        self._icon = None

        self._file_extension = None
        self._macro_extension = None

        tmp = scriptinfo()

        self._executable = tmp['name']
        self._executable_directory = tmp['dir']
        self._frozen = tmp['frozen']

        self._directory = None
        self._filename = ''

        self._dpi = 0

        self._app_data_path = None
        self._settings_file = None
        self._default_settings_file = None

        self._release_file = None
        self._beta_file = None

        self._app = None
        """:type: PyQt5.QtWidgets.QApplication.QApplication"""

        self._main_window = None
        """:type: PyQt5.QtWidgets.QMainWindow.QMainWindow"""

        self._main_data = None

        self.dispatcher = CommandDispatcher()

        ##############################################################################

        self._msgs = []

        self.message = MrSignal()
        self.msg = MrSignal()

        self._read_config()

        self.picking_manager = None
        """:type: fem.gui.vtk_widget.vtk_graphics.picking.PickingManager"""

    def register_picking_manager(self, picking_manager):
        self.picking_manager = picking_manager

    def database_exe(self):
        return self._database_exe

    def application_name(self):
        return self._application_name

    def major_version(self):
        return self._major_version

    def minor_version(self):
        return self._minor_version

    def micro_version(self):
        return self._micro_version

    def other_version(self):
        return self._other_version

    def user_manual(self):
        return self._user_manual

    def email_recipient(self):
        return self._email_recipient

    def long_name(self):
        return self._long_name

    def date_created(self):
        return self._date_created

    def date_modified(self):
        return self._date_modified

    def author(self):
        return self._author

    def description(self):
        return self._description

    def icon(self):
        return self._icon

    def file_extension(self):
        return self._file_extension

    def macro_extension(self):
        return self._macro_extension

    def executable(self):
        return self._executable

    def executable_directory(self):
        return self._executable_directory

    def frozen(self):
        return self._frozen

    def directory(self):
        # type: () -> str
        if self._directory is None:
            return self.home_directory()

        return self._directory

    def set_directory(self, directory):
        # type: (str) -> None
        directory = os.path.dirname(os.path.realpath(str(directory)))

        assert os.path.isdir(directory)

        self._directory = directory

    def filename(self):
        # type: () -> str
        return self._filename

    def set_filename(self, filename):
        # type: (str) -> None
        self.set_directory(filename)
        self._filename = filename

    def dpi(self):
        return self._dpi

    def app_data_path(self):
        return self._app_data_path

    def settings_file(self):
        return self._settings_file

    def default_settings_file(self):
        if os.path.isfile(self._default_settings_file):
            return self._default_settings_file

        return None

    def release_file(self):
        return self._release_file

    def beta_file(self):
        return self._beta_file

    def app(self):
        if self._app is None:
            self._app = QtWidgets.QApplication([])
            w = QtWidgets.QWidget()
            self._dpi = w.logicalDpiX()

            if self._dpi != 96:
                font = self._app.font()
                font.setPixelSize(13)
                self._app.setFont(font)

        return self._app

    def set_icon(self):
        self.app().setWindowIcon(QtGui.QIcon(self._icon))

    def main_window(self):
        return self._main_window

    def register_main_window(self, mw):
        self._main_window = mw
        try:
            self.dispatcher.register_main_window(mw)
        except AttributeError:
            pass

    def main_data(self):
        return self._main_data

    def register_main_data(self, md):
        self._main_data = md

    def version(self):
        if self._other_version == '':
            return self._major_version, self._minor_version, self._micro_version
        else:
            return self._major_version, self._minor_version, self._micro_version, self._other_version

    def application_version(self):
        return ('%d.%d.%d %s' %
                (self._major_version, self._minor_version, self._micro_version, self._other_version)).strip()

    def program_name(self):
        # type: () -> str
        return '%s %s' % (self._application_name, self.application_version())

    def application_info(self):
        # _data_roles = OrderedDict()
        data = {}

        data['Application Name'] = self._application_name
        data['Application Version'] = self.application_version()

        ts = timestamp().split(' ')

        data['Date'] = ts[0]
        data['Time'] = ts[1]
        data['User ID'] = self.user_id()

        return data

    def window_title(self):
        # type: () -> str
        if self._filename is None:
            filename = "*"
        else:
            filename = self._filename

        if not self.dispatcher.undo_stack.isClean():
            filename += "*"

        return "%s - [%s]" % (self.program_name(), filename)

    def user_id(self):
        return getpass.getuser()

    @staticmethod
    def home_directory():
        # type: () -> str
        return os.path.expanduser('~')

    def view_label(self):
        # type: () -> str
        if self._filename is None:
            filename = '*'
        else:
            filename = self._filename

        return '%s\n%s\n%s' % (self.program_name(), filename, timestamp())

    def about(self):
        about_txt = """
        Program Name: %s
        Version: %s
        Description: %s

        Author: %s
        Date Created: %s
        Date Modified: %s
        """ % (self._long_name, self.application_version(), self._description, self._author,
               self._date_created, self._date_modified)

        return about_txt

    @staticmethod
    def file_in_use(filename):
        if os.path.exists(filename):
            # noinspection PyBroadException
            try:
                os.rename(filename, filename + '_')
                os.rename(filename + '_', filename)
                return False
            except Exception:
                return True

        return False

    def info_message(self, msg):
        # type: (str) -> None
        self.msg.emit('Info: %s' % msg)

    def push_error(self, msg):
        self._msgs.append('Error: %s' % msg)

    def push_info(self, msg):
        self._msgs.append('Info: %s' % msg)

    def flush_msgs(self):
        for msg in self._msgs:
            self.msg.emit(msg)

        del self._msgs[:]

    def clear_msgs(self):
        del self._msgs[:]

    def error_message(self, msg):
        # type: (str) -> None
        self.msg.emit('Error: %s' % msg)

    def _read_config(self):

        config_file = self.config_file

        if config_file is None:
            return

        # config_file = 'configuration.%s.%d.%d.%d.json' % (
        #     self.config_app_name, self._major_version, self._minor_version, self._micro_version
        # )
        # config_file = os.path.join(self.config_directory, config_file)

        with open(config_file, 'r') as f:
            data = json.load(f)

        application = data['application']

        self._author = application['author']
        self._date_created = application['date_created']
        self._date_modified = application['date_modified']
        self._description = application['description']
        self._long_name = application['long_name']
        self._application_name = application['application_name']

        version = application['version']

        major = version['major']
        minor = version['minor']
        micro = version['micro']
        other = version['other']

        files = data['files']

        self._release_file = files['release_file']
        self._beta_file = files['beta_file']
        self._icon = files['icon']
        self._user_manual = files['user_manual']
        # self._default_settings_file = files['default_settings_file']

        feedback = data['feedback']

        self._email_recipient = feedback['email_recipient']

        extensions = data['extensions']

        self._file_extension = extensions['file_extension']
        self._macro_extension = extensions['macro_extension']

        # self._database_exe = data['plugins']['punch_database']

        self._app_data_path = os.getenv('APPDATA') + r'\StressApps\%s' % self._application_name.lower()

        assert (major, minor, micro, other) == (self._major_version, self._minor_version, self._micro_version,
                                                self._other_version)

        self.set_icon()

        return data


#######################


def timestamp():
    # type: () -> str
    return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())


def scriptinfo():
    '''
    Returns a dictionary with information about the running top level Python
    script:
    ---------------------------------------------------------------------------
    dir:    directory containing script or compiled executable
    name:   name of script or executable
    source: name of source code file
    ---------------------------------------------------------------------------
    "name" and "source" are identical if and only if running interpreted code.
    When running code compiled by py2exe or cx_freeze, "source" contains
    the name of the originating Python script.
    If compiled by PyInstaller, "source" contains no meaningful information.
    '''

    import os, sys, inspect
    # ---------------------------------------------------------------------------
    # scan through call stack for caller information
    # ---------------------------------------------------------------------------
    for teil in inspect.stack():
        # skip system calls
        if teil[1].startswith("<"):
            continue
        if teil[1].upper().startswith(sys.exec_prefix.upper()):
            continue
        trc = teil[1]

    # trc contains highest level calling script name
    # check if we have been compiled
    if getattr(sys, 'frozen', False):
        scriptdir, scriptname = os.path.split(sys.executable)
        return {"dir": scriptdir,
                "name": scriptname,
                "source": trc,
                "frozen": True}

    # from here on, we are in the interpreted case
    scriptdir, trc = os.path.split(trc)
    # if trc did not contain directory information,
    # the current working directory is what we need
    if not scriptdir:
        scriptdir = os.getcwd()

    scr_dict = {"name": trc,
                "source": trc,
                "dir": scriptdir,
                "frozen": False}
    return scr_dict


if __name__ == '__main__':
    print(Configuration.instance())
    print(BaseApp.BaseConfiguration.instance())
    print(BaseApp.BaseConfiguration.instance())
    print(BaseApp.BaseConfiguration.instance())
    print(Configuration.instance())
    print(Configuration.instance())
    print(Configuration.instance())

    assert BaseApp.BaseConfiguration.instance() is Configuration.instance()
