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

    # _dispatchers = {}
    #
    # def __new__(cls, dispatcher_id):
    #
    #     if dispatcher_id in cls._dispatchers:
    #         raise Exception('CommandDispatcher3: dispatcher id %s already exists!' % dispatcher_id)
    #
    #     cls._dispatchers[dispatcher_id] = super(CommandDispatcher, cls).__new__(dispatcher_id)

    def __init__(self, dispatcher_id=None):

        self.dispatcher_id = dispatcher_id

        self.main_window = None
        """:type: QtGui.QWidget"""

        self._undo_stack = UndoStack()
        self._action_history = []

        self._actions = {}
        self._commands = {}

        self._parent_dispatcher = None
        """:type: CommandDispatcher"""

        self._children_dispatchers = {}

        self._action_added = MrSignal()

        self._action_data = None

    @property
    def undo_stack(self):
        try:
            return self._parent_dispatcher.undo_stack
        except AttributeError:
            return self._undo_stack

    @property
    def action_history(self):
        try:
            return self._parent_dispatcher.action_history
        except AttributeError:
            return self._action_history

    @property
    def action_added(self):
        try:
            return self._parent_dispatcher.action_added
        except AttributeError:
            return self._action_added

    def add_child(self, dispatcher):
        try:
            assert dispatcher.dispatcher_id not in self._children_dispatchers
        except AssertionError:
            debuginfo((dispatcher.dispatcher_id, list(self._children_dispatchers.keys())))
            raise

        self._children_dispatchers[dispatcher.dispatcher_id] = dispatcher

        dispatcher.set_parent(self)

    def set_parent(self, parent_dispatcher):
        self._parent_dispatcher = parent_dispatcher

    def multiple_dispatch(self, actions):
        for action in actions:
            self.dispatch(action)

    def _get_action(self, action):
        try:
            i1 = action.index('(')
        except ValueError:
            return action, '()'

        action_name = action[:i1]

        action_data = action[i1:]

        # if action_data.beginswith("'"):
        #     action_data = action_data[1:-1]

        try:
            action_data = literal_eval(action_data)
        # except SyntaxError:
        #     pass
        except Exception:
            raise TypeError('CommandDispatcher3: Action applied_loads_data cannot be created! %s' % action_data)

        try:
            action = self._actions[action_name]
        except KeyError:
            raise TypeError('CommandDispatcher3: Action %s not found in defined actions!' % str(action_name))

        if self._action_data is None:
            action_data = action.ActionDataCls(*action_data)
        else:
            action_data = self._action_data

        action = action(action_data)

        return action

    def _get_command(self, action):
        # debuginfo('get command', 1)
        if isinstance(action, str):

            # debuginfo('get command', 2)

            action = self._get_action(action)

            # debuginfo('get command', 21)

            if action is None:
                return None

            action_name = action.action_name

            try:
                command = self._commands[action_name](action)
            except KeyError:
                raise TypeError('CommandDispatcher3: Command %s not found in defined actions!' % str(action_name))

            return command

        elif isinstance(action, Action):

            # debuginfo('get command', 3)

            action_name = action.action_name

            try:
                command = self._commands[action_name](action)
            except KeyError:
                raise TypeError('CommandDispatcher3: Command %s not found in defined actions!' % str(action_name))

            return command

        elif isinstance(action, (Command, ChildCommand)):
            # debuginfo('get command', 4)
            return action

        elif isinstance(action, tuple):
            # debuginfo('get command', 5)
            try:
                action_data = literal_eval(str(action[1]))
            except IndexError:
                action_data = None

            action_name = action[0]
            try:
                # noinspection PyPep8Naming
                Action_ = self._actions[action_name]
            except KeyError:
                raise TypeError('CommandDispatcher3: Action type not valid! %s' % str(action))

            if action_data is None:
                action = Action_()
            else:
                action_data = Action_.ActionDataCls(*action_data)
                action = Action_(action_data)

            try:
                # noinspection PyPep8Naming
                Command_ = self._commands[action_name]
            except KeyError:
                raise TypeError('CommandDispatcher3: Action type not valid! %s' % str(action))

            command = Command_(action)
            return command

        raise TypeError('CommandDispatcher3: Action type not valid! %s' % str(action))

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

    def _action_str(self, action):

        if isinstance(action, str):
            if action.upper() in ('REDO', 'UNDO'):
                return action

        else:
            action = str(self._get_command(action).action)

        if self.dispatcher_id is not None:
            return '%s.%s' % (self.dispatcher_id, action)
        else:
            return action

    def _dispatch(self, action, tracking=True):
        if isinstance(action, Command):
            self._action_data = action.action.action_data
        elif isinstance(action, Action):
            self._action_data = action.action_data

        action_str = self._action_str(action)

        # debuginfo(self.dispatcher_id, '_dispatch', action_str)

        try:
            return self._parent_dispatcher._dispatch(action_str, tracking)
        except AttributeError:
            return self.dispatch(action_str, tracking, False, action_str)

    def _encapsulate_command(self, command):
        try:
            return self._parent_dispatcher._encapsulate_command(command)
        except AttributeError:
            return command

    def dispatch(self, action, tracking=True, traceback=True, action_str=None):

        # debuginfo(action)

        if traceback is True and self._parent_dispatcher is not None:
            return self._dispatch(action, tracking)

        try:
            assert isinstance(action, (str, tuple))
        except AssertionError:
            debuginfo(action.__class__.__name__)
            raise

        if self._try_undo_redo(action):
            return True

        if isinstance(action, str):

            i1 = action.index('(')
            action_name = action[:i1]
            action_data = action[i1:]

            if '.' in action_name:
                # try:
                tmp = action_name.split('.')
                # noinspection SpellCheckingInspection
                childname = tmp[0]

                action_ = '.'.join(tmp[1:]) + action_data

                # print(self.dispatcher_id, childname, action_)

                try:
                    # debuginfo(
                    #     'Calling child dispatcher {%s} from {%s}. {%s} {%s}' % (
                    #         childname, self.dispatcher_id, action_, action_str
                    #     )
                    # )
                    return self._children_dispatchers[childname].dispatch(action_, tracking, False, action_str)
                except KeyError:
                    debuginfo('###########################################')
                    debuginfo(self.dispatcher_id, childname, action, action_)
                    debuginfo(list(self._children_dispatchers.keys()))
                    debuginfo('###########################################')
                    raise

        # except AttributeError:
        #     pass

        # print(1, self.dispatcher_id, action)

        command = self._get_command(action)

        # print(2)

        if command is None:
            return False

        command = self._encapsulate_command(command)

        # print(3)

        command.skip_first = False
        command.redo()
        command_result = command.command_result
        command.skip_first = True

        # print(4)

        self._action_data = None

        # TODO: not sure if this is the desired behavior
        if command_result is False:
            return False

        action_ = command.action

        if action_.log_action is True and tracking is True:
            if action_str is None:
                action_str = str(action_)
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
                raise Exception("CommandDispatcher3: Missing commands! %s" % str(action_keys - command_keys))
            else:
                raise Exception("CommandDispatcher3: Missing actions! %s" % str(command_keys - action_keys))

        for key, child in iteritems(self._children_dispatchers):
            child.verify()

    def finalize(self):
        self._parent_dispatcher = None
        self._actions.clear()
        self._commands.clear()

        for key, child in iteritems(self._children_dispatchers):
            child.finalize()

        self._children_dispatchers.clear()

    def __call__(self, action_name):
        def add_action(cls):

            if issubclass(cls, Action):
                self._actions[action_name] = cls
            elif issubclass(cls, Command):
                self._commands[action_name] = cls
            else:
                raise TypeError("CommandDispatcher3: %s is not an Action or Command!" % cls.__name__)

            cls.action_name = action_name

            return cls

        return add_action
