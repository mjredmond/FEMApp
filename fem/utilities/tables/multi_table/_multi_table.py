"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range

from ast import literal_eval

from ..basic_table import BasicTable

from qtpy import QtWidgets, QtCore, QtGui

from ..table_data import TableDataList


from fem.utilities.command_dispatcher import CommandDispatcher, ChildCommand, Action, Command, dispatcher_version
from fem.utilities import MrSignal
from fem.utilities.debug import debuginfo, show_stack_trace


assert dispatcher_version == '3'


class _ChildCommand(ChildCommand):
    def __init__(self, command, widget, data_id):
        # debuginfo(1)
        super(_ChildCommand, self).__init__(command)

        # debuginfo(2)

        self.widget = widget
        """:type: MultiTable"""

        self.data_id = data_id

        # debuginfo(3)

        # debuginfo(self.data_id)

        self.main_data = self.widget.get_data(self.data_id)

        # debuginfo(4)

        # debuginfo(self.main_data)

    def redo(self):
        if self.command.skip_first:
            self.command.skip_first = False
            return

        if self.main_data is not None:
            self.command.action.main_data = self.main_data
            self.widget.activate(self.data_id)
            self.command.redo()

            # FIXME: when the command fails, the widget is still activated... not desired

    def undo(self):
        if self.main_data is not None:
            self.widget.activate(self.data_id)
            self.command.undo()


# 1. catch action
# 2. encapsulate with data id attached
# 3. perform action


class _CommandDispatcher(CommandDispatcher):
    def __init__(self, widget):
        super(_CommandDispatcher, self).__init__()

        self.widget = widget
        """:type: MultiTable"""

        self._data_id = ''

    def _wrap_command(self, command):

        # debuginfo('encapsulate')

        command = _ChildCommand(command, self.widget, self._data_id)

        return self._parent_dispatcher._wrap_command(command)

    def _action_str(self, action):
        try:
            i1 = action.index('(')
        except ValueError:
            i1 = -1

        data_id = self.widget.current_data_id()

        if i1 == -1:
            action += "('%s')" % data_id
        else:
            action = "%s('%s', %s)" % (action[:i1], data_id, action[i1+1:-1])

        if self.dispatcher_id is not None:
            action = '%s.%s' % (self.dispatcher_id, action)

        self._data_id = data_id

        return action

        # return super(_CommandDispatcher, self)._action_str(str(action))

    def _get_action(self, action):
        # debuginfo('MultiTable', 1)
        try:
            i1 = action.index('(')
        except ValueError:
            return action, '()'

        # debuginfo('MultiTable', 2)

        action_name = action[:i1]
        action_data = action[i1:]

        try:
            action_data = literal_eval(action_data)
        except Exception:
            raise TypeError('CommandDispatcher3: Action applied_loads_data cannot be created! %s' % action_data)

        # debuginfo('MultiTable', 3)

        try:
            action = self._actions[action_name]
        except KeyError:
            raise TypeError('CommandDispatcher3: Action %s not found in defined actions!' % str(action_name))

        # debuginfo('MultiTable', 4)

        data_id = action_data[0]
        action_data = action_data[1:]

        # debuginfo('MultiTable', data_id)

        if self._action_data is None:
            action_data = action.ActionDataCls(*action_data)
        else:
            action_data = self._action_data
            self._action_data = None

        action = action(action_data)

        return action

    def dispatch(self, action, tracking=True, traceback=True, action_str=None):
        # debuginfo('MultiTable dispatch', action, tracking, traceback, action_str)
        return super(_CommandDispatcher, self).dispatch(action, tracking, traceback, action_str)


class MultiTable(QtWidgets.QWidget):

    MainData_1 = TableDataList
    MainData_2 = TableDataList

    main_data_1 = None
    main_data_2 = None

    def __init__(self, parent=None, dispatcher_id=None, id_1='Table1', id_2='Table2'):
        super(MultiTable, self).__init__(parent)

        class _Table1(BasicTable):
            MainData = self.MainData_1
            main_data = self.main_data_1

        class _Table2(BasicTable):
            MainData = self.MainData_2
            main_data = self.main_data_2

        self.table_1 = _Table1(self)
        self.table_1.dispatcher.dispatcher_id = id_1

        self.table_2 = _Table2(self)
        self.table_2.dispatcher.dispatcher_id = id_2

        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._splitter.addWidget(self.table_1)
        self._splitter.addWidget(self.table_2)

        self._layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(self._layout)

        self._layout.addWidget(self._splitter)

        self.table_1.table_1.row_changed.connect(self._row_changed)

        self.dispatcher = _CommandDispatcher(self)
        self.dispatcher.dispatcher_id = dispatcher_id

        self.dispatcher.add_child(self.table_1.dispatcher)
        self.dispatcher.add_child(self.table_2.dispatcher)

        self.request_focus = MrSignal()

        self.data = {}
        """:type: dict[str, TableDataList]"""

    def _row_changed(self, row):
        try:
            data_id = self.table_1.main_data[row].id
        except IndexError:
            return

        if data_id == '':
            return

        try:
            data = self.data[data_id]
        except KeyError:
            data = self.data[data_id] = self.MainData_2()

        self.table_2.set_main_data(data)

    def current_data_id(self):
        try:
            return self.table_1.main_data[self.table_1.table_1.current_index()[0]].id
        except IndexError:
            return None

    def get_data(self, data_id):
        # debuginfo(self.data)
        return self.data.get(data_id, None)

    # @show_stack_trace
    def activate(self, data_id):

        # debuginfo('activate', 1)

        ids = self.table_1.main_data.ids()

        # debuginfo('activate', 2)

        try:
            index = ids.index(data_id)
        except ValueError:
            return

        # debuginfo('activate', 3)

        # debuginfo('MultiTable set selection and index')

        self.table_1.table_1.set_selection_and_index([[index, 0]])

        # debuginfo('activate', 4)

        self.request_focus.emit()

    def update_all(self):
        self.table_1.update_all()
        self.table_2.update_all()
