"""
command_dispatacher.command_dispatcher

Defines command dispatcher

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets
import inspect

from .action import Action, ActionData
from .command import Command, ChildCommand
from .undo_stack import UndoStack
from .action_signal import ActionSignal, MrSignal

from six import iteritems

from fem.utilities.debug import debuginfo, show_stack_trace

import warnings
import sys

from ast import literal_eval


class CommandDispatcher(object):
    def __init__(self):
        self.main_window = None
        """:type: QtGui.QWidget"""

        self.undo_stack = UndoStack()
        self.action_history = []

        self._macro_on = False

        self._actions = {}
        self._commands = {}

        self._parent_dispatcher = None
        """:type: CommandDispatcher"""

        self._prefix = None

        self.action_added = MrSignal()

        self._focus_method = None

    def set_focus_method(self, focus_method):
        self._focus_method = focus_method

    def set_prefix(self, prefix):
        self._prefix = prefix

    def register_parent_dispatcher(self, parent_dispatcher, prefix=None):
        self._parent_dispatcher = parent_dispatcher
        """:type: CommandDispatcher"""

        if prefix is None:
            prefix = self._prefix

        self._parent_dispatcher.add_actions_and_commands(prefix, self._actions, self._commands)

        if prefix is not None:
            self._prefix = prefix

    def add_actions_and_commands(self, prefix, actions, commands):

        if prefix is not None:
            for action_name, action in iteritems(actions):
                action_name = '%s.%s' % (prefix, action_name)
                action.action_name = action_name
                self._actions[action_name] = action

            for command_name, command in iteritems(commands):
                command_name = '%s.%s' % (prefix, command_name)
                command.command_name = command_name
                self._commands[command_name] = command
        else:
            for action_name, action in iteritems(actions):
                self._actions[action_name] = action

            for command_name, command in iteritems(commands):
                self._commands[command_name] = command

        self.verify()

    def begin_macro(self, msg="No msg available"):
        if self._macro_on is True:
            raise Exception("Macro is already on!!!")

        self._macro_on = True
        self.undo_stack.beginMacro(msg)

    def end_macro(self):
        self._macro_on = False
        self.undo_stack.endMacro()

    def multiple_dispatch(self, actions):
        for action in actions:
            self.dispatch(action)

    def _get_command(self, action):
        if isinstance(action, str):

            try:
                i1 = action.index('(')
            except ValueError:
                return None

            action_name = action[:i1]
            action_data = action[i1:]

            try:
                action = self._actions[action_name]
            except KeyError:
                raise TypeError('CommandDispatcher2: Action %s not found in defined actions!' % str(action_name))

            try:
                action_data = literal_eval(action_data)
            except Exception:
                raise TypeError('CommandDispatcher2: Action applied_loads_data cannot be created! %s' % action_data)

            action_data = action.ActionDataCls(*action_data)

            action = action(action_data)

            try:
                command = self._commands[action_name](action)
            except KeyError:
                raise TypeError('CommandDispatcher2: Command %s not found in defined actions!' % str(action_name))

            return command

        elif isinstance(action, Action):
            action_name = action.action_name

            try:
                command = self._commands[action_name](action)
            except KeyError:
                raise TypeError('CommandDispatcher2: Command %s not found in defined actions!' % str(action_name))

            return command

        elif isinstance(action, (Command, ChildCommand)):
            return action

        elif isinstance(action, tuple):
            try:
                action_data = literal_eval(str(action[1]))
            except IndexError:
                action_data = None

            action_name = action[0]
            try:
                Action_ = self._actions[action_name]
            except KeyError:
                raise TypeError('CommandDispatcher2: Action type not valid! %s' % str(action))

            if action_data is None:
                action = Action_()
            else:
                action_data = Action_.ActionDataCls(*action_data)
                action = Action_(action_data)

            try:
                Command_ = self._commands[action_name]
            except KeyError:
                raise TypeError('CommandDispatcher2: Action type not valid! %s' % str(action))

            command = Command_(action)
            return command

        raise TypeError('CommandDispatcher2: Action type not valid! %s' % str(action))

    # def child_dispatch(self, action, tracking=True):
    #     command = self._get_command(action)
    #     command = ChildCommand(command, self._focus_method)
    #     self.dispatch(command, tracking)

    def _try_undo_redo(self, action):
        if isinstance(action, str):
            tmp = action.upper()

            if tmp == 'UNDO':
                self.action_history.append('Undo')
                self.action_added.emit(action)
                self.undo_stack.undo()
                return True
            elif tmp == 'REDO':
                self.action_history.append('Redo')
                self.action_added.emit(action)
                self.undo_stack.redo()
                return True

        return False

    def undo(self):
        self.dispatch('Undo')

    def redo(self):
        self.dispatch('Redo')

    def dispatch(self, action, tracking=True):
        if self._parent_dispatcher is not None:
            assert self._prefix is not None

            if isinstance(action, str):
                tmp = action.upper()
                if tmp not in ('UNDO', 'REDO'):
                    action = '%s.%s' % (self._prefix, action)

            return self._parent_dispatcher.dispatch(action, tracking)

        if self._try_undo_redo(action):
            return True

        command = self._get_command(action)

        command.skip_first = False
        command.redo()
        command_result = command.command_result
        command.skip_first = True

        # TODO: not sure if this is the desired behavior
        if command_result is False:
            return False

        action = command.action

        if self._macro_on is False and action.log_action is True and tracking is True:
            action_str = str(action)
            self.action_history.append(action_str)
            # this notifies the main window that an action has been added, so that it can update the log
            self.action_added.emit(action_str)

        # if the action is successful, push it to the stack (it will be skipped on first push)
        if command_result is True:
            if command.push_to_stack and tracking is True:

                self.undo_stack.push(command)

                if command.set_clean is True:
                    self.undo_stack.setClean()

            return True
        else:
            return False

    def verify(self):

        action_keys = set(self._actions.keys())
        command_keys = set(self._commands.keys())

        if action_keys != command_keys:
            if len(action_keys) > len(command_keys):
                raise Exception("Missing commands! %s" % str(action_keys - command_keys))
            else:
                raise Exception("Missing actions! %s" % str(command_keys - action_keys))

    def finalize(self):
        self._parent_dispatcher = None
        self._actions.clear()
        self._commands.clear()

    def __call__(self, action_name):
        def add_action(cls):

            if issubclass(cls, Action):
                self._actions[action_name] = cls
            elif issubclass(cls, Command):
                self._commands[action_name] = cls
            else:
                raise TypeError("%s is not an Action or Command!" % cls.__name__)

            cls.action_name = action_name

            return cls

        return add_action
