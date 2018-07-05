from __future__ import print_function, absolute_import

from qtpy import QtCore

from fem.base_app.configuration import BaseConfiguration
from fem.utilities.dock_table.validation_context_menu import validation_context_menu

from fem.utilities.command_dispatcher import Action, Command, ActionData

import os

cd_type = os.environ.get('CommandDispatcherVersion', '1')


########################################################################################################################

class FileReadActionData(ActionData):
    def __init__(self, filename, *args):
        super(FileReadActionData, self).__init__(*args)

        self.filename = filename

    def __str__(self):
        return "('%s',)" % self.filename

    def split(self):
        return None, str((self.filename,))


# noinspection PyAbstractClass
class BaseFileReadAction(Action):
    """
    Action for reading an input file.
    """

    action_name = None
    ActionDataCls = FileReadActionData

    data_id = None
    log_action = True

    BaseConfiguration = None
    """:type: BaseConfiguration"""

    BaseMainData = None

    if cd_type == '1':
        def __init__(self, main_data, action_data):
            super(BaseFileReadAction, self).__init__(main_data, action_data)

            self.config = self.BaseConfiguration.instance()

            self.old_filename = self.config.filename()
            self.old_data = self.main_data.serialize()

            self.new_data = None

            self._validate()

    else:
        def __init__(self, action_data):
            super(BaseFileReadAction, self).__init__(action_data)

            self.main_data = self.BaseMainData.instance()

            self.config = self.BaseConfiguration.instance()

            self.old_filename = self.config.filename()
            self.old_data = self.main_data.serialize()

            self.new_data = None

            self._validate()

    def _validate(self):
        try:
            self.new_data = self.main_data.read_from_file(self.action_data.filename)
            self.is_valid = True
        except Exception as e:
            self.is_valid = False

    def _before_redo(self):
        pass

    def _redo(self):
        if self.new_data is None:
            return False

        self.main_data.set_data(self.new_data)

        return True

    def _after_redo(self):
        self.config.set_filename(self.action_data.filename)

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.set_data(self.old_data)

    def _after_undo(self):
        self.config.set_filename(self.old_filename)


class BaseFileReadCommand(Command):
    """
    Command for reading an input file.
    """

    set_clean = True

    def _after_redo(self):
        self._get_main_window().update_all()

    def _after_undo(self):
        self._after_redo()

    def _before_undo(self):
        pass

    def _before_redo(self):
        pass

########################################################################################################################


class FileSaveActionData(ActionData):
    def __init__(self, filename, *args):
        super(FileSaveActionData, self).__init__(*args)

        self.filename = filename

    def __str__(self):
        return "('%s',)" % self.filename

    def split(self):
        return None, str((self.filename,))


# noinspection PyAbstractClass
class BaseFileSaveAction(Action):
    """
    Action for saving a file.
    """

    action_name = None
    ActionDataCls = FileSaveActionData

    data_id = None
    log_action = True

    BaseConfiguration = None
    """:type: BaseConfiguration"""

    BaseMainData = None

    if cd_type == '1':
        def __init__(self, main_data, action_data):
            super(BaseFileSaveAction, self).__init__(main_data, action_data)

            self.config = self.BaseConfiguration.instance()

            self.old_filename = self.config.filename()
            """:type: str"""

    else:
        def __init__(self, action_data):
            super(BaseFileSaveAction, self).__init__(action_data)

            self.main_data = self.BaseMainData.instance()

            self.config = self.BaseConfiguration.instance()

            self.old_filename = self.config.filename()
            """:type: str"""

    def _validate(self):
        self.is_valid = True

    def _before_redo(self):
        pass

    def _redo(self):
        # noinspection PyBroadException

        #try:
        self.main_data.save_to_file(self.action_data.filename)
        #except Exception as e:
        #    self.config.push_error('%s: Unable to save file.' % self.action_name)
        #    return False

        return True

    def _after_redo(self):
        self.config.set_filename(self.action_data.filename)

    def _before_undo(self):
        pass

    def _undo(self):
        pass

    def _after_undo(self):
        self.config.set_filename(self.old_filename)


class BaseFileSaveCommand(Command):
    """
    Command for saving a file.
    """

    set_clean = True

    def _after_redo(self):
        self._get_main_window().update_window_title()

    def _after_undo(self):
        self._after_redo()

    def _before_redo(self):
        pass

    def _before_undo(self):
        pass

########################################################################################################################


class FileCloseActionData(ActionData):
    def __init__(self, filename, *args):
        super(FileCloseActionData, self).__init__(*args)

        self.filename = filename

    def __str__(self):
        return "('%s',)" % self.filename

    def split(self):
        return None, str((self.filename,))


# noinspection PyAbstractClass
class BaseFileCloseAction(Action):
    """
    Action for closing the current file.
    """

    action_name = None
    ActionDataCls = FileCloseActionData

    data_id = None
    log_action = True

    BaseConfiguration = None
    """:type: BaseConfiguration"""

    BaseMainData = None

    def __init__(self, *args):
        super(BaseFileCloseAction, self).__init__(*args)

        self.main_data = self.BaseMainData.instance()

        self.config = self.BaseConfiguration.instance()

        self.old_data = self.main_data.serialize()

    def _redo(self):
        self.main_data.clear()
        return True

    def _undo(self):
        self.main_data.set_data(self.old_data)

    def _before_redo(self):
        pass

    def _after_redo(self):
        self.config.set_filename(None)

    def _before_undo(self):
        pass

    def _after_undo(self):
        self.config.set_filename(self.action_data.filename)


class BaseFileCloseCommand(Command):
    """
    Command for closing the current file.
    """

    set_clean = True

    def _after_redo(self):
        self._get_main_window().update_all()

    def _after_undo(self):
        self._after_redo()

    def _before_undo(self):
        pass

    def _before_redo(self):
        pass

########################################################################################################################


# noinspection PyPep8Naming
def _register(cls, BaseConfiguration_):
    class _Tmp(cls):
        BaseConfiguration = BaseConfiguration_

    _Tmp.__name__ = cls.__name__

    return _Tmp


class FileActionData(object):
    FileReadActionData = FileReadActionData
    FileSaveActionData = FileSaveActionData
    FileCloseActionData = FileCloseActionData

    @classmethod
    def register_config(cls, BaseConfiguration):
        cls.FileCloseActionData = _register(cls.FileCloseActionData, BaseConfiguration)
        cls.FileSaveActionData = _register(cls.FileSaveActionData, BaseConfiguration)
        cls.FileCloseActionData = _register(cls.FileCloseActionData, BaseConfiguration)

    @classmethod
    def copy_cls(cls):
        # noinspection PyClassHasNoInit
        class _Tmp(cls):
            pass

        _Tmp.__name__ = cls.__name__

        return _Tmp


class BaseFileActions(object):
    BaseFileReadAction = BaseFileReadAction
    BaseFileSaveAction = BaseFileSaveAction
    BaseFileCloseAction = BaseFileCloseAction

    # noinspection PyPep8Naming,PyTypeChecker
    @classmethod
    def register_config(cls, BaseConfiguration_):
        cls.BaseFileReadAction = _register(cls.BaseFileReadAction, BaseConfiguration_)
        cls.BaseFileSaveAction = _register(cls.BaseFileSaveAction, BaseConfiguration_)
        cls.BaseFileCloseAction = _register(cls.BaseFileCloseAction, BaseConfiguration_)

    @classmethod
    def register_main_data(cls, BaseMainData_):
        cls.BaseFileReadAction.BaseMainData = BaseMainData_
        cls.BaseFileSaveAction.BaseMainData = BaseMainData_
        cls.BaseFileCloseAction.BaseMainData = BaseMainData_

    @classmethod
    def copy_cls(cls):
        class _Tmp(cls):
            pass

        _Tmp.__name__ = cls.__name__

        return _Tmp


class BaseFileCommands(object):
    BaseFileReadCommand = BaseFileReadCommand
    BaseFileSaveCommand = BaseFileSaveCommand
    BaseFileCloseCommand = BaseFileCloseCommand

    # noinspection PyPep8Naming,PyTypeChecker
    @classmethod
    def register_config(cls, BaseConfiguration_):
        cls.BaseFileReadCommand = _register(cls.BaseFileReadCommand, BaseConfiguration_)
        cls.BaseFileSaveCommand = _register(cls.BaseFileSaveCommand, BaseConfiguration_)
        cls.BaseFileCloseCommand = _register(cls.BaseFileCloseCommand, BaseConfiguration_)

    @classmethod
    def register_main_window(cls, MainWindow):
        cls.BaseFileReadCommand.MainWindow = MainWindow
        cls.BaseFileSaveCommand.MainWindow = MainWindow
        cls.BaseFileCloseCommand.MainWindow = MainWindow

    @classmethod
    def copy_cls(cls):
        # noinspection PyClassHasNoInit
        class _Tmp(cls):
            pass

        _Tmp.__name__ = cls.__name__

        return _Tmp
