"""
command_dispatacher.command_dispatcher

Defines command dispatcher

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets
import inspect

from .action import Action, ActionData
from .command import Command
from .undo_stack import UndoStack
from .action_signal import ActionSignal, MrSignal

from six import iteritems

from fem.utilities.debug import debuginfo

import warnings


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

    def set_prefix(self, prefix):
        self._prefix = prefix

    def register_parent_dispatcher(self, parent_dispatcher, prefix=None):
        self._parent_dispatcher = parent_dispatcher
        """:type: CommandDispatcher"""

        if prefix is None:
            prefix = self._prefix

        self._parent_dispatcher.add_actions_and_commands(prefix, self._actions, self._commands)

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

    def register_main_window(self, main_window):
        assert isinstance(main_window, QtWidgets.QWidget)
        self.main_window = main_window
        self.undo_stack.setParent(self.main_window)

    def multiple_dispatch(self, actions):
        for action in actions:
            self.dispatch(action)

    def _get_action(self, data):
        if isinstance(data, Command):
            action_ = data.action
        elif isinstance(data, (tuple, list)):
            action_ = list(data)
            if isinstance(action_[0], Action):
                action_ = action_[0]
            elif isinstance(action_[0], str):
                if action_[0] not in self._actions:
                    raise TypeError('Action %s not found in defined actions!' % str(action_[0]))


        elif isinstance(data, Action):
            action_ = data
        elif isinstance(data, str):
            if data not in self._actions:
                raise TypeError('Action %s not found in defined actions!' % str(data))
            action_ = self._actions[data]()
        else:
            raise TypeError('CommandDispatcher._get_action: wrong _data_roles type! %s' % str(data))

        return action_

    def _apply_prefix(self, action):
        if isinstance(action, Command):
            action.command_name = '%s.%s' % (self._prefix, action.command_name)
            action_ = action.action

        elif isinstance(action, list):
            action_ = action[0]

            if isinstance(action_, str):
                action[0] = '%s.%s' % (self._prefix, action[0])
                return

            if len(action) == 3:
                assert isinstance(action[2], Command)
                action[2].command_name = '%s.%s' % (self._prefix, action[2].command_name)

        elif isinstance(action, Action):
            action_ = action

        else:
            raise TypeError('CommandDispatcher._apply_prefix: wrong _data_roles type! %s' % str(action))

        assert isinstance(action_, Action)
        action_.action_name = '%s.%s' % (self._prefix, action_.action_name)

        # FIXME: this is a bug, repeated prefix
        tmp = action_.action_name.split('.')
        if len(tmp) > 1 and tmp[0] == tmp[1]:
            action_.action_name = '.'.join(tmp[1:])

    def dispatch(self, action, tracking=True):
        if self._parent_dispatcher is not None:
            assert self._prefix is not None

            if isinstance(action, tuple):
                action = list(action)

            print(action[0])
            self._apply_prefix(action)
            print(action[0])

            return self._parent_dispatcher.dispatch(action, tracking)

        # if self.main_window is None:
        #     warnings.warn("CommandDispatcher: main_window is None!")

        action_ = None

        if isinstance(action[0], Action):
            action_ = action[0]
            action_name = action_.action_name
        elif isinstance(action, (tuple, list)):
            action_name = action[0]
        elif isinstance(action, str):
            action_name = action
        else:
            raise ValueError('CommandDispatcher.dispatch: unknown action type! %s' % str(action))

        tmp = action_name.upper()
        if tmp == 'UNDO':
            self.action_history.append('Undo')
            self.action_added.emit(action_name)
            self.undo_stack.undo()
            return
        elif tmp == 'REDO':
            self.action_history.append('Redo')
            self.action_added.emit(action_name)
            self.undo_stack.redo()
            return

        if action_name not in self._actions:
            raise TypeError('Action %s not found in defined actions!' % str(action_name))

        if action_name not in self._commands:
            raise TypeError('Action %s not found in defined commands!' % str(action_name))

        action_data = action[1]

        if not isinstance(action_data, ActionData):
            try:
                action_data = action[1]
            except IndexError:
                action_data = ActionData()

            assert isinstance(action_data, (ActionData, tuple))

        if action_ is None:
            action_ = self._actions[action_name](self.main_window.get_model(), action_data)

        if len(action) == 3:
            command = action[2]
            assert isinstance(command, Command)
        else:
            command = self._commands[action_name](self.main_window, action_)

        command.skip_first = False
        command.redo()
        command_result = command.command_result
        command.skip_first = True

        # TODO: not sure if this is the desired behavior
        if command.command_result is False:
            return

        if self._macro_on is False and action_.log_action is True and tracking is True:
            action_str = str(action_)
            self.action_history.append(action_str)
            # this notifies the main window that an action has been added, so that it can update the log
            self.action_added.emit(action_str)

        if command_result is True:  # if the action is successful, push it to the stack (it will be skipped on first push)
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

    def make_connections(self, obj, obj_name=None, signals=()):
        """
        :type obj: QtGui.QWidget
        """

        if obj_name is None:
            obj_name = obj.__class__.__name__

        def _make_connection(action):

            obj_signal = getattr(obj, action)

            if not isinstance(obj_signal, MrSignal):
                debuginfo(obj_signal)
                raise TypeError("Not a Signal!!!")

            action_name = "%s.%s" % (obj_name, action)

            def _connection(*args):
                return self.dispatch((action_name, args))

            _connection.__name__ = "%s_%s" % (obj_name, action)

            obj_signal.connect(_connection)
            setattr(obj, _connection.__name__, _connection)

        if signals == ():
            signals = [signal for signal in dir(obj) if isinstance(getattr(obj, signal), ActionSignal)]

        for signal_id in signals:
            _make_connection(signal_id)

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
