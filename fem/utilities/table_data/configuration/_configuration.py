"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from ..actions import Actions, Commands
from fem.utilities.command_dispatcher import CommandDispatcher


class Configuration(object):
    def __init__(self):
        self._dispatcher = CommandDispatcher()

        Actions.attach(self._dispatcher)
        Commands.attach(self._dispatcher)

    def set_dispatcher(self, dispatcher, prefix=None):
        self._dispatcher.register_parent_dispatcher(dispatcher, prefix)
        self._dispatcher.set_prefix(prefix)

    def set_prefix(self, prefix):
        self._dispatcher.set_prefix(prefix)

    def dispatch(self, *args):
        self._dispatcher.dispatch(*args)
