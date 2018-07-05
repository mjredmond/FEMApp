"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range

from .command_dispatcher import CommandDispatcher


# noinspection PyProtectedMember
class CommandDispatcherWrapper(CommandDispatcher):
    def __init__(self, dispatcher_id):
        super(CommandDispatcherWrapper, self).__init__(dispatcher_id)

        self._dispatcher = None

    @property
    def dispatcher_id(self):
        return self._dispatcher.dispatcher_id

    def add_child(self, dispatcher):
        self._dispatcher = dispatcher
        self._dispatcher.set_parent(self)

    def dispatch(self, *args):
        return self._dispatcher.dispatch(*args)

    def _dispatch(self, *args):
        return self._dispatcher._dispatch(*args)

    def _final_dispatch(self, *args):
        return self._dispatcher._final_dispatch(*args)

    def _action_str(self, action, action_data=None):
        return action
