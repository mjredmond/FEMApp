"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from ..actions import get_actions, get_commands, get_actions_2, get_commands_2

from fem.utilities.command_dispatcher import CommandDispatcher, dispatcher_version


assert dispatcher_version == '3'


class Configuration(object):
    def __init__(self, dispatcher_id):
        self.dispatcher = CommandDispatcher(dispatcher_id)

        self.Actions = get_actions()
        self.Commands = get_commands()
        self.Actions2 = get_actions_2()
        self.Commands2 = get_commands_2()

        self.Actions.attach(self.dispatcher)
        self.Commands.attach(self.dispatcher)
        self.Actions2.attach(self.dispatcher)
        self.Commands2.attach(self.dispatcher)

    def dispatch(self, *args):
        self.dispatcher.dispatch(*args)
