"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from ..actions import get_actions, get_commands

from ._dispatcher import _CommandDispatcher

from fem.utilities.debug import debuginfo


# class _CommandDispatcher(CommandDispatcher):
#     def __init__(self, *args):
#         super(_CommandDispatcher, self).__init__(*args)
#
#     def _action_str(self, action, action_data=None):
#


class Configuration(object):
    def __init__(self, dispatcher_id):

        # debuginfo(dispatcher_id)

        try:
            assert dispatcher_id != ''
        except AssertionError:
            raise AssertionError('Dispatcher needs a name!')

        self.dispatcher = _CommandDispatcher(dispatcher_id)

        self.Actions = get_actions()
        self.Commands = get_commands()

        self.Actions.attach(self.dispatcher)
        self.Commands.attach(self.dispatcher)

    def dispatch(self, *args):
        self.dispatcher.dispatch(*args)
