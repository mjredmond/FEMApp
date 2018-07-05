from __future__ import print_function, absolute_import

from ..base_app import BaseApp
from ..configuration import config

BaseFileActions = BaseApp.BaseActions.BaseFileActions
BaseFileCommands = BaseApp.BaseCommands.BaseFileCommands


dispatcher = config.dispatcher

########################################################################################################################


@dispatcher('File.read')
class FileReadAction(BaseFileActions.BaseFileReadAction):
    pass


@dispatcher('File.read')
class FileReadCommand(BaseFileCommands.BaseFileReadCommand):
    pass


########################################################################################################################


@dispatcher('File.save')
class FileSaveAction(BaseFileActions.BaseFileSaveAction):
    pass


@dispatcher('File.save')
class FileSaveCommand(BaseFileCommands.BaseFileSaveCommand):
    pass


########################################################################################################################


@dispatcher('File.close')
class FileCloseAction(BaseFileActions.BaseFileCloseAction):
    pass


@dispatcher('File.close')
class FileCloseCommand(BaseFileCommands.BaseFileCloseCommand):
    pass
