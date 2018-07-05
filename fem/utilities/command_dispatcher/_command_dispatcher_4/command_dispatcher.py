"""
command_dispatacher.command_dispatcher

Defines command dispatcher

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from weakref import ref, WeakValueDictionary

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

    count = 0

    def __init__(self, dispatcher_id=None):

        try:
            self.dispatcher_id = dispatcher_id
        except AttributeError:
            pass

        self.main_window = None
        """:type: QtGui.QWidget"""

        self._undo_stack = UndoStack()
        self._action_history = []

        self._actions = {}
        self._commands = {}

        self._parent_dispatcher = None
        """:type: ref[CommandDispatcher]"""

        self._children_dispatchers = WeakValueDictionary()

        self._action_added = MrSignal()

        self._main_data = None

        self.main_data_can_change = True

    @property
    def main_data(self):
        return self._main_data

    @main_data.setter
    def main_data(self, value):
        if self.main_data_can_change:
            self._main_data = value

    @property
    def undo_stack(self):
        try:
            return self._parent_dispatcher().undo_stack
        except (TypeError, AttributeError):
            return self._undo_stack

    @property
    def action_history(self):
        try:
            return self._parent_dispatcher().action_history
        except (TypeError, AttributeError):
            return self._action_history

    @property
    def action_added(self):
        try:
            return self._parent_dispatcher().action_added
        except (TypeError, AttributeError):
            return self._action_added

    def clear_children(self):
        self._children_dispatchers.clear()

    def add_child(self, dispatcher):

        if dispatcher.dispatcher_id is None:
            CommandDispatcher.count += 1
            dispatcher.dispatcher_id = str(CommandDispatcher.count)

        if dispatcher.dispatcher_id in self._children_dispatchers:
            assert self._children_dispatchers[dispatcher.dispatcher_id] is dispatcher
            return

        self._children_dispatchers[dispatcher.dispatcher_id] = dispatcher

        dispatcher.set_parent(self)

    def set_parent(self, parent_dispatcher):
        self._parent_dispatcher = ref(parent_dispatcher)

    def multiple_dispatch(self, actions):
        for action in actions:
            self.dispatch(action)

    def _get_command(self, action):

        if isinstance(action, Action):
            action_name = action.action_name

            try:
                command = self._commands[action_name](action, main_window=self.main_window)
            except KeyError:
                raise TypeError('CommandDispatcher4: Command %s not found in defined actions!' % str(action_name))

        elif isinstance(action, (Command, ChildCommand)):
            command = action
            command.main_window = self.main_window

        else:
            raise TypeError('CommandDispatcher4: Action type not valid! %s' % str(action))

        return command

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

    def _subdata(self, data):
        return self.main_data.subdata(data)

    def _action_str(self, action, action_data=None):

        assert isinstance(action, str)

        if action.upper() in ('REDO', 'UNDO'):
            return action

        # debuginfo(self.dispatcher_id, self._parent_dispatcher)

        if None not in (self.dispatcher_id, self._parent_dispatcher):
            if action_data is not None:
                data = action_data.split()

                # debuginfo(22222, data)

                if data[0] is None and data[1] is None:
                    action = '%s.%s()' % (self.dispatcher_id, action)
                elif data[0] is None:
                    action = '%s.%s%s' % (self.dispatcher_id, action, data[1])
                elif data[1] is None:
                    action = '%s[%s].%s()' % (self.dispatcher_id, data[0], action)
                else:
                    action = '%s[%s].%s%s' % (self.dispatcher_id, data[0], action, data[1])

            else:
                action = '%s.%s' % (self.dispatcher_id, action)

        return action

    def dispatch(self, action, tracking=True):

        if self._try_undo_redo(action):
            return True

        try:
            action_name, action_data = action
            action_name = action_name.replace('.', '_')
        except (TypeError, ValueError):
            assert isinstance(action, str)
            action_info = self.parse_action(action)
            # debuginfo(action_info)
            return self._dispatch(action_info, tracking, action)

        if not isinstance(action_data, tuple):
            action_data = (action_data,)

        try:
            action_cls = self._actions[action_name]
        except KeyError:
            raise TypeError('CommandDispatcher4: Action type not valid! %s' % str(action_name))

        action_data = action_cls.ActionDataCls(*action_data)

        try:
            # debuginfo('getting action_str')
            action_str = self._action_str(action_name, action_data)
            # debuginfo(1111111, action_str)
            return self._parent_dispatcher()._traceback(action_str, tracking, action_data)
        except (TypeError, AttributeError):
            action_str = '%s%s' % (action_name, str(action_data))
            action_info = self.parse_action(action_str)
            return self._dispatch(action_info, tracking, action_str, action_data)

    def _traceback(self, action, tracking=True, action_data=None):

        action_str = self._action_str(action)

        try:
            return self._parent_dispatcher()._traceback(action_str, tracking, action_data)
        except (TypeError, AttributeError):
            action_info = self.parse_action(action_str)
            # debuginfo(action_str)
            return self._dispatch(action_info, tracking, action_str, action_data)

    def _dispatch(self, action_info, tracking, action_str, action_data=None):
        _dispatches, _action = action_info

        # debuginfo(action_info)

        if len(_dispatches) == 0:
            action_name, action_data_ = _action

            if action_data is None:
                action_data = action_data_

            # if not isinstance(action_data, tuple):
            #     action_data = (action_data,)

            return self._final_dispatch(action_name, action_data, action_str, tracking)

        dispatcher_id, dispatcher_data = _dispatches[0]

        # debuginfo(action_info)

        if self.dispatcher_id is not None:
            try:
                assert dispatcher_id == self.dispatcher_id
            except AssertionError:
                print('This dispatcher = %s, other dispatcher = %s' % (self.dispatcher_id, dispatcher_id))
                raise

            try:
                dispatcher_id = _dispatches[1][0]
            except IndexError:
                _action_info = [], _action
                return self._dispatch(_action_info, tracking, action_str, action_data)

        else:
            return self._children_dispatchers[dispatcher_id]._dispatch(action_info, tracking, action_str, action_data)

        # debuginfo(self.dispatcher_id, list(self._children_dispatchers.keys()))
        dispatcher = self._children_dispatchers[dispatcher_id]

        # FIXME: should the dispatcher be responsible for this?  might be taken care of by the commands

        if dispatcher_data is not None:

            subdata = self._subdata(dispatcher_data)
        else:
            subdata = None

        old_main_data = dispatcher.get_model

        if subdata is not None:
            dispatcher.get_model = subdata

        _action_info = _dispatches[1:], _action

        # noinspection PyProtectedMember
        dispatch_result = dispatcher._dispatch(_action_info, tracking, action_str, action_data)

        dispatcher.get_model = old_main_data

        return dispatch_result

    def _final_dispatch(self, action_name, action_data, action_str, tracking=True):

        # debuginfo(action_str)

        if self._try_undo_redo(action_name):
            return True

        try:
            action_cls = self._actions[action_name]
        except KeyError:
            raise TypeError('CommandDispatcher4: Action type not valid! %s' % str(action_name))

        if isinstance(action_data, tuple):
            action_data = action_cls.ActionDataCls(*action_data)

        assert isinstance(action_data, action_cls.ActionDataCls)

        action = action_cls(action_data)
        action.get_model = self.main_data

        command = self._get_command(action)

        if command is None:
            return False

        command = self._wrap_command(command)

        command.skip_first = False
        command.redo()
        command_result = command.command_result
        command.skip_first = True

        # TODO: not sure if this is the desired behavior
        if command_result is False:
            command.finalize()
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

    def _wrap_command(self, command):
        try:
            return self._parent_dispatcher()._wrap_command(command)
        except (TypeError, AttributeError):
            return command

    def verify(self):

        action_keys = set(self._actions.keys())
        command_keys = set(self._commands.keys())

        if action_keys != command_keys:
            if len(action_keys) > len(command_keys):
                raise Exception("CommandDispatcher4: Missing commands! %s" % str(action_keys - command_keys))
            else:
                raise Exception("CommandDispatcher4: Missing actions! %s" % str(command_keys - action_keys))

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
        action_name = action_name.replace('.', '_')

        def add_action(cls):

            if issubclass(cls, Action):
                self._actions[action_name] = cls
            elif issubclass(cls, Command):
                self._commands[action_name] = cls
            else:
                raise TypeError("CommandDispatcher4: %s is not an Action or Command!" % cls.__name__)

            cls.action_name = action_name

            return cls

        return add_action

    @staticmethod
    def parse_action(s):

        # debuginfo(s)

        tmp = s
        data = ''

        if s[-1] == ')':
            count = 1

            for i in range(1, len(s)):
                a = s[-i-1]

                if a == ')':
                    count += 1

                elif a == '(':
                    count -= 1

                if count == 0:
                    j = len(s) - i - 1

                    data_ = s[j + 1:-1]
                    if data_ != '':
                        data = literal_eval(data_)
                    else:
                        data = []

                    tmp = s[:j]

                    break

        tmp = tmp.split('.')

        # debuginfo(tmp, data)

        tmp_ = tmp[:-1]

        _tmp = []

        for i in tmp_:
            a = i.split('[')
            b = a[0]
            try:
                c = literal_eval(a[1][:-1])
            except IndexError:
                c = None

            _tmp.append((b, c))

        try:
            insert_data = _tmp[-1][1]
            _tmp[-1] = _tmp[-1][0], None

            if insert_data is not None:
                try:
                    data.insert(0, insert_data)
                    data = tuple(data)
                except AttributeError:
                    data = tuple([insert_data, data])

            else:
                data = tuple([data])

        except IndexError:
            data = tuple(data)

        # debuginfo(_tmp, (tmp[-1], data))

        return _tmp, (tmp[-1], data)
