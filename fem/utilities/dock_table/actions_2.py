"""
dock_table.actions_2

Actions for secondary dock table

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

import numpy as np

from qtpy import QtCore

from base_app.configuration import BaseConfiguration
from fem.utilities.command_dispatcher import Action, Command, ActionData
from fem.utilities.dock_table.validation_context_menu import validation_context_menu

from .actions import TableCommand, TableAction


config = BaseConfiguration.instance()


########################################################################################################################


class TableActionData2(ActionData):
    def __init__(self, index1, index2, *args):
        super(TableActionData2, self).__init__(*args)

        self.index1 = index1  # (row1, column1)
        """:type: tuple[int, int]"""

        self.index2 = index2  # (row1, column1)
        """:type: tuple[int, int]"""

    def __str__(self):
        raise NotImplementedError


class TableAction2(Action):
    action_name = None
    ActionDataCls = None

    data_id = None
    log_action = True

    def __init__(self, main_data, action_data):
        super(TableAction2, self).__init__(main_data, action_data)

        self.main_data = main_data
        """:type: model.main_data.MainData"""

        self.data = getattr(self.main_data, self.data_id)

        self.subdata = self.data.subdata(self.action_data.index1[1])

    def _redo(self):
        raise NotImplementedError

    def _undo(self):
        raise NotImplementedError

    def _before_redo(self):
        pass

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True

########################################################################################################################


class TableAddActionData2(TableActionData2):
    def __str__(self):
        return str(str(self.index1), str(self.index2))


class TableAddAction2(TableAction2):
    action_name = None
    ActionDataCls = TableAddActionData2

    def __init__(self, *args):
        super(TableAddAction2, self).__init__(*args)

        self.removed_data = None

    def _redo(self):
        if self.removed_data is not None:
            self.subdata.add(self.removed_data)

        elif self.subdata.add() is None:
            return False

        return True

    def _undo(self):
        self.removed_data = self.subdata.remove(-1)


class TableAddCommand2(TableCommand):
    def _after_redo(self):
        dock = self._dock
        dock.table2.update_all()

        dock.table1.select(self.action.action_data.index1)
        dock.table2.select_last_row()

        self._raise_dock()

########################################################################################################################


class TableRemoveActionData2(TableActionData2):
    def __str__(self):
        return str(str(self.index1), str(self.index2))


class TableRemoveAction2(TableAction2):
    action_name = None
    ActionDataCls = TableRemoveActionData2

    def __init__(self, *args):
        super(TableRemoveAction2, self).__init__(*args)

        self.removed_data = None

    def _redo(self):
        self.removed_data = self.subdata.remove(self.action_data.index2[0])

        if self.removed_data is None:
            return False

        return True

    def _undo(self):
        if self.removed_data is None:
            return

        self.subdata.insert(self.action_data.index2[0], self.removed_data)


class TableRemoveCommand2(TableCommand):
    def _after_redo(self):
        dock = self._dock
        dock.table2.update_all()

        dock.table1.select(self.action.action_data.index1)
        dock.table2.select(self.action.action_data.index2)

        self._raise_dock()

########################################################################################################################


class TableInsertActionData2(TableActionData2):
    def __str__(self):
        return str(str(self.index1), str(self.index2))


class TableInsertAction2(TableAction2):
    action_name = None
    ActionDataCls = TableInsertActionData2

    def __init__(self, *args):
        super(TableInsertAction2, self).__init__(*args)

        self.inserted_data = None

    def _redo(self):
        if self.inserted_data is not None:
            self.subdata.insert(self.action_data.index2[0], self.inserted_data)
            return True

        self.inserted_data = self.subdata.insert(self.action_data.index2[0])

        if self.inserted_data is None:
            return False

        return True

    def _undo(self):
        if self.inserted_data is None:
            return

        self.subdata.remove(self.action_data.index2[0])


class TableInsertCommand2(TableCommand):
    def _after_redo(self):
        dock = self._dock
        dock.table2.update_all()

        dock.table1.select(self.action.action_data.index1)
        dock.table2.select(self.action.action_data.index2)

        self._raise_dock()


########################################################################################################################


class TableSetDataActionData2(TableActionData2):
    def __init__(self, index1, index2, new_data, *args, **kwargs):
        super(TableSetDataActionData2, self).__init__(index1, index2, *args)

        """
        key_pressed: -1 = No key pressed
        key_pressed: 0 = Return
        key_pressed: 1 = Tab
        """

        self.new_data = new_data

        try:
            key_pressed = kwargs['key_pressed']
        except KeyError:
            key_pressed = None

        if key_pressed in (QtCore.Qt.Key_Return, QtCore.Qt.EnterKeyReturn):
            self.key_pressed = 0
        elif key_pressed == QtCore.Qt.Key_Tab:
            self.key_pressed = 1
        elif key_pressed is None:
            self.key_pressed = -1
        else:
            raise ValueError('TableSetDataActionData2: Key not recognized!')

    def __str__(self):
        return str(str(self.index1), str(self.index2), str(self.new_data))


class TableSetDataAction2(TableAction2):
    action_name = None
    ActionDataCls = TableSetDataActionData2

    def __init__(self, *args):
        super(TableSetDataAction2, self).__init__(*args)

        self.old_data = None
        self.state_diff = None
        self.is_valid = False

        self._validate()

    def _validate(self):
        self.is_valid = True

    def _redo(self):
        row2, column2 = self.action_data.index2
        self.old_data = self.subdata[row2][column2]
        self.subdata[row2][column2] = self.action_data.new_data
        new_data = self.subdata[row2][column2]

        if new_data != self.old_data:
            return True
        else:
            return False

    def _undo(self):
        row2, column2 = self.action_data.index2
        self.subdata[row2][column2] = self.old_data


class TableSetDataCommand2(TableCommand):
    def __init__(self, *args):
        super(TableSetDataCommand2, self).__init__(*args)

        self._count = 0

    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()
        dock.table2.update_all()

        if self._count == 0:
            offset = 1
        else:
            offset = 0

        self._count += 1

        row1, col1 = self.action.action_data.index1
        row2, col2 = self.action.action_data.index2
        key_pressed = self.action.action_data.key_pressed

        max_row = dock.table2.row_count()
        max_col = dock.table2.colum_count()

        if key_pressed == 0:
            row2 += offset
        elif key_pressed == 1:
            col2 += offset

        if row2 >= max_row:
            row2 = max_row - 1

        if col2 >= max_col:
            col2 = max_col - 1

        dock.table1.select((row1, col1))
        dock.table2.select((row2, col2))

        self._raise_dock()

########################################################################################################################


def str_to_list(data):

    if isinstance(data, list):
        return data

    tmp = data.split('\n')

    result = []

    for tmp_ in tmp:
        result.append(tmp_.split('\t'))

    return result


class TablePasteActionData2(TableActionData2):
    def __init__(self, index1, index2, selection, new_data, *args):
        super(TablePasteActionData2, self).__init__(index1, index2, *args)

        self.selection = selection  # [(row1, col1), (row2, col2)]
        """:type: list[tuple[int]]"""

        self.new_data = new_data

    def __str__(self):
        return str(str(self.index1), str(self.index2), str(tuple(map(str, self.selection))), str(self.new_data))


class TablePasteAction2(TableAction2):
    action_name = None
    ActionDataCls = TablePasteActionData2
    SetData = None

    def __init__(self, *args):
        super(TablePasteAction2, self).__init__(*args)

        self._actions = []

        self.new_data = []

        self._validate()

    def _validate(self):
        selection = self.action_data.selection

        (row1, col1), (row2, col2) = selection

        selected_row_count = row2 - row1 + 1
        selected_col_count = col2 - col1 + 1

        self.new_data = str_to_list(self.action_data.new_data)

        paste_rows = len(self.new_data)

        if paste_rows == 0:
            self.is_valid = False
            return

        paste_cols = len(self.new_data[0])

        if selected_row_count < paste_rows or selected_col_count < paste_cols:
            selected_row_count = paste_rows
            selected_col_count = paste_cols

        elif selected_row_count % paste_rows != 0 or selected_col_count % paste_cols != 0:
            selected_row_count = paste_rows
            selected_col_count = paste_cols

        row2 = row1 + selected_row_count - 1
        col2 = col1 + selected_col_count - 1

        table_rows = len(self.subdata)
        table_columns = len(self.subdata[0])

        if row2 >= table_rows or col2 >= table_columns:
            self.is_valid = False
            config.error_message('TablePasteAction2: Cannot paste outside of range!')
            return

        repeat_rows = selected_row_count // paste_rows
        repeat_cols = selected_col_count // paste_cols

        a = np.array(self.new_data)

        b = np.concatenate([a] * repeat_rows)
        c = np.concatenate([b] * repeat_cols, axis=1)

        self.new_data = c.tolist()

        self.is_valid = True

    def _redo(self):
        index1 = self.action_data.index1
        [(first_row2, first_column2), (last_row2, last_column2)] = self.action_data.selection

        min_size = min(len(self.new_data), len(self.subdata))

        for i in range(min_size):
            row = first_row2 + i

            data_i = self.new_data[i]

            for j in range(len(data_i)):
                column = first_column2 + j

                data_ij = data_i[j]

                action_data = self.ActionDataCls(index1, (row, column), data_ij)
                action = self.SetData(self.main_data, action_data)
                self._actions.append(action)
                action.redo()

        return True

    def _undo(self):
        for action in reversed(self._actions):
            action.undo()

        self._actions = []


class TablePasteCommand2(TableCommand):
    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()
        dock.table2.update_all()

        # noinspection PyUnusedLocal
        (first_row, first_column), (last_row, last_column) = self.action.action_data.selection

        dock.table1.select(self.action.action_data.index1)
        dock.table2.select((first_row, first_column))

        self._raise_dock()

########################################################################################################################


class TableSetRowsActionData2(TableActionData2):
    def __init__(self, index1, index2, row_count, *args):
        super(TableSetRowsActionData2, self).__init__(index1, index2, *args)

        self.row_count = row_count

    def __str__(self):
        return str(tuple(map(str, (self.index1, self.index2, self.row_count,))))


class TableSetRowsAction2(TableAction2):
    action_name = None
    ActionDataCls = TableSetRowsActionData2
    Add = None
    Remove = None

    def __init__(self, *args):
        super(TableSetRowsAction2, self).__init__(*args)

        self.old_row_count = len(self.subdata)

        self._actions = []

        self.action_success = []

    def _redo(self):
        new_row_count = self.action_data.row_count

        if new_row_count == self.old_row_count:
            return False

        self._actions = []

        self.action_success = []

        if new_row_count > self.old_row_count:
            diff = new_row_count - self.old_row_count

            index1 = self.action_data.index1
            index2 = self.action_data.index2

            ActionDataCls = self.Add.ActionDataCls

            for i in range(diff):
                action = self.Add(self.main_data, ActionDataCls(index1, index2))
                self._actions.append(action)
                self.action_success.append(action.redo())

        else:
            diff = self.old_row_count - new_row_count

            last_index = len(self.subdata) - 1

            index1 = self.action_data.index1
            index2 = self.action_data.index2

            ActionDataCls = self.Remove.ActionDataCls

            for i in range(diff):
                action = self.Remove(self.main_data, ActionDataCls(index1, index2))
                last_index -= 1
                self._actions.append(action)
                self.action_success.append(action.redo())

        if False in self.action_success:
            self._undo()
            return False

        return True

    def _undo(self):
        action_success = list(reversed(self.action_success))
        actions = list(reversed(self._actions))

        for i in range(len(actions)):
            if action_success[i]:
                actions[i].undo()

        self._actions = []
        self.action_success = []


class TableSetRowsCommand2(TableCommand):
    def __init__(self, *args):
        super(TableSetRowsCommand2, self).__init__(*args)

        self._added = None
        self._removed = None

    def _after_redo(self):
        dock = self._dock
        dock.table2.update_all()

        dock.table1.select(self.action.action_data.index1)
        dock.table2.select(self.action.action_data.index2)

        self._raise_dock()

########################################################################################################################


class TableUpDownActionData2(TableActionData2):
    def __str__(self):
        return str(tuple(map(str, (self.index1, self.index2,))))
    
    
class TableUpDownAction2(TableAction2):
    action_name = None
    ActionDataCls = TableUpDownActionData2
    offset = 0

    def __init__(self, *args):
        super(TableUpDownAction2, self).__init__(*args)

        pass

    def _redo(self):
        current_row = self.action_data.index2[0]    
        new_row = current_row + self.offset

        data = self.subdata

        if new_row < 0 or new_row >= len(data):
            return False

        data_index = data[current_row]
        data_index_m1 = data[new_row]

        data[current_row] = data_index_m1
        data[new_row] = data_index

        return True

    def _undo(self):
        current_row = self.action_data.index2[0]    
        new_row = current_row + self.offset

        data = self.subdata

        data_index = data[current_row]
        data_index_m1 = data[new_row]

        data[current_row] = data_index_m1
        data[new_row] = data_index

    def new_row(self):
        current_row = self.action_data.index2[0]
        return current_row + self.offset

    def new_index(self):
        current_row = self.action_data.index2[0]
        return current_row + self.offset, self.action_data.index2[1]


class TableUpAction2(TableUpDownAction2):
    offset = -1


class TableDownAction2(TableUpDownAction2):
    offset = 1


class TableUpDownCommand2(TableCommand):
    def __init__(self, *args):
        super(TableUpDownCommand2, self).__init__(*args)

        self.action = self.action
        """:type: TableUpDownAction2"""

    def _after_redo(self):
        dock = self._dock
        dock.table2.update_all()
        dock.table2.select(self.action.new_index())

        self._raise_dock()

    def _after_undo(self):
        dock = self._dock
        dock.table2.update_all()
        dock.table2.select(self.action.action_data.index2)

        self._raise_dock()


class TableUpCommand2(TableUpDownCommand2):
    pass


class TableDownCommand2(TableUpDownCommand2):
    pass

########################################################################################################################


class TableRightClickActionData2(TableActionData2):
    def __str__(self):
        return str(tuple(map(str, (self.index1, self.index2,))))


class TableRightClickAction2(TableAction2):
    action_name = None
    ActionDataCls = TableRightClickActionData2
    log_action = False

    def __init__(self, *args):
        super(TableRightClickAction2, self).__init__(*args)

        self.validation_data = []

    def _redo(self):
        index1 = self.action_data.index1
        index2 = self.action_data.index2
        self.validation_data = self.main_data.validation_data_2(self.data, index1, index2)

        return True

    def _undo(self):
        pass


class TableRightClickCommand2(TableCommand):
    push_to_stack = False
    set_data_action = None

    def __init__(self, *args):
        super(TableRightClickCommand2, self).__init__(*args)

        self.action = self.action
        """:type: TableRightClickAction2"""

    def _after_redo(self):
        success, (data, index) = validation_context_menu(self.action.validation_data)
        if success:
            index1 = self.action.action_data.index1
            index2 = self.action.action_data.index2
            config.dispatcher.dispatch((self.set_data_action, TableSetDataActionData2(index1, index2, str(data))))

########################################################################################################################


class TableActions2(object):
    TableAddAction2 = TableAddAction2
    TableDownAction2 = TableDownAction2
    TableInsertAction2 = TableInsertAction2
    TablePasteAction2 = TablePasteAction2
    TableRemoveAction2 = TableRemoveAction2
    TableRightClickAction2 = TableRightClickAction2
    TableSetDataAction2 = TableSetDataAction2
    TableSetRowsAction2 = TableSetRowsAction2
    TableUpAction2 = TableUpAction2


class TableCommands2(object):
    TableAddCommand2 = TableAddCommand2
    TableDownCommand2 = TableDownCommand2
    TableInsertCommand2 = TableInsertCommand2
    TablePasteCommand2 = TablePasteCommand2
    TableRemoveCommand2 = TableRemoveCommand2
    TableRightClickCommand2 = TableRightClickCommand2
    TableSetDataCommand2 = TableSetDataCommand2
    TableSetRowsCommand2 = TableSetRowsCommand2
    TableUpCommand2 = TableUpCommand2
