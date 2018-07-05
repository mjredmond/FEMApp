"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range

from fem.utilities.debug import debuginfo

from fem.utilities.command_dispatcher import CommandDispatcher, ChildCommand, dispatcher_version


assert dispatcher_version == '4'


class _ChildCommand(ChildCommand):
    def __init__(self, command, table, index, main_window):
        super(_ChildCommand, self).__init__(command)

        self.table = table
        self.index = index
        self._main_window = main_window

    def redo(self):
        if self.command.skip_first:
            self.command.skip_first = False
            return

        # debuginfo('redo', self.index)

        self.table.set_selection_and_index([self.index])
        self._main_window.force_update(self.index)
        self.command.redo()

    def undo(self):
        self.table.set_selection_and_index([self.index])
        self._main_window.force_update(self.index)
        self.command.undo()


class _CommandDispatcher(CommandDispatcher):

    def __init__(self, dispatcher_id):
        super(_CommandDispatcher, self).__init__(dispatcher_id)

        self.table = None

    @property
    def main_data(self):
        return self.main_window.get_model

    @main_data.setter
    def main_data(self, value):
        pass

    def _subdata(self, data):
        subdata = self.main_data.subdata(data)

        index = self.main_data.get_index(data)

        if index is not None:
            self.table.selection_changed.block()
            self.table.set_selection_and_index([index])
            self.table.selection_changed.unblock()
            self.main_window.force_update(index)

        return subdata

    def _wrap_command(self, command):
        index = self.table.current_index()
        command = _ChildCommand(command, self.table, index, self.main_window)

        return super(_CommandDispatcher, self)._wrap_command(command)

    def _action_str(self, action, action_data=None):

        tmp = '%s[%s].%s' % (self.dispatcher_id, str(self.table.current_index())[1:-1], action)

        if action_data is not None:
            data = action_data.split()

            if data[1] is not None:
                if data[1][0] != '(':
                    data_ = '(%s)' % data[1]
                else:
                    data_ = data[1]

                tmp = '%s%s' % (tmp, data_)

        # debuginfo(tmp)

        return tmp
