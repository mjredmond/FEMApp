"""
BaseApp was originaly a standalone package that was used to create skeleton apps quickly.  It no longer makes senese
in the current context where it is included with the FemApp.
"""
from __future__ import print_function, absolute_import

from .configuration import BaseConfiguration
from .gui import BaseMainWindow
from .actions import BaseActions, BaseCommands


def get_base_app():
    class BaseApp(object):
        BaseMainWindow = BaseMainWindow.copy_cls()
        BaseActions = BaseActions.copy_cls()
        BaseCommands = BaseCommands.copy_cls()
        BaseConfiguration = BaseMainWindow.BaseConfiguration
        BaseModel = BaseMainWindow.BaseModel
        BaseFileMenu = BaseMainWindow.BaseFileMenu
        BaseEditMenu = BaseMainWindow.BaseEditMenu
        BaseViewMenu = BaseMainWindow.BaseViewMenu
        BaseHelpMenu = BaseMainWindow.BaseHelpMenu
        BaseBetaMenu = BaseMainWindow.BaseBetaMenu
        BaseLoggingDock = BaseMainWindow.BaseLoggingDock

    # noinspection PyPep8Naming
    BaseMainWindow_ = BaseApp.BaseMainWindow

    BaseApp.BaseConfiguration = BaseMainWindow_.BaseConfiguration
    BaseApp.BaseModel = BaseMainWindow_.BaseModel
    BaseApp.BaseFileMenu = BaseMainWindow_.BaseFileMenu
    BaseApp.BaseEditMenu = BaseMainWindow_.BaseEditMenu
    BaseApp.BaseViewMenu = BaseMainWindow_.BaseViewMenu
    BaseApp.BaseHelpMenu = BaseMainWindow_.BaseHelpMenu
    BaseApp.BaseBetaMenu = BaseMainWindow_.BaseBetaMenu
    BaseApp.BaseLoggingDock = BaseMainWindow_.BaseLoggingDock

    BaseApp.BaseActions.register_config(BaseApp.BaseConfiguration)
    BaseApp.BaseActions.register_main_data(BaseApp.BaseModel)

    BaseApp.BaseCommands.register_config(BaseApp.BaseConfiguration)
    BaseApp.BaseCommands.register_main_window(BaseApp.BaseMainWindow)

    return BaseApp


BaseApp = get_base_app()
