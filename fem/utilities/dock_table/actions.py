"""
dock_table.actions

Actions for main dock table

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

import numpy as np

from qtpy import QtCore

from base_app.configuration import BaseConfiguration
from fem.utilities.command_dispatcher import Action, Command, ActionData
from fem.utilities.dock_table.validation_context_menu import validation_context_menu


config = BaseConfiguration.instance()


########################################################################################################################


class TableActionData(ActionData):
    def __init__(self, index, *args):
        super(TableActionData, self).__init__(*args)

        self.index = index  # (row, column)
        """:type: tuple[int, int]"""

    def __str__(self):
        raise NotImplementedError


class TableAction(Action):
    action_name = None
    ActionDataCls = None

    data_id = None
    log_action = True

    def __init__(self, main_data, action_data):
        super(TableAction, self).__init__(main_data, action_data)

        self.main_data = main_data
        """:type: model.main_data.MainData"""

        self.data = getattr(self.main_data, self.data_id)

        # self._validate()

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


class TableCommand(Command):
    dock_id = None

    def __init__(self, *args):
        super(TableCommand, self).__init__(*args)

        self._dock = getattr(self.main_window, self.dock_id)
        """:type: utilities.dock_table.dock_table.DockTable"""

    def _before_redo(self):
        pass

    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()
        dock.table1.select_last_row()

        self._raise_dock()

    def _before_undo(self):
        pass

    def _after_undo(self):
        self._after_redo()

    def _raise_dock(self):
        tab_widget = self.main_window.model_data_dock.tab_widget
        index = tab_widget.indexOf(self._dock)
        tab_widget.setCurrentIndex(index)

        self.main_window.model_data_dock.raise_()


########################################################################################################################

class TableAddActionData(TableActionData):
    def __str__(self):
        return '()'


class TableAddAction(TableAction):
    action_name = None
    ActionDataCls = TableAddActionData

    def __init__(self, *args):
        super(TableAddAction, self).__init__(*args)

        self.removed_data = None

    def _redo(self):
        if self.removed_data is not None:
            self.data.add(self.removed_data)

        elif self.data.add() is None:
            return False

        return True

    def _undo(self):
        self.removed_data = self.data.remove(-1)


class TableAddCommand(TableCommand):
    def __init__(self, *args):
        super(TableAddCommand, self).__init__(*args)

    def _after_redo(self):
        self._dock.table1.select_last_row()

########################################################################################################################


class TableSelectAndEditActionData(TableActionData):
    def __init__(self, index, data_id, *args):
        super(TableSelectAndEditActionData, self).__init__(index, *args)

        self.data_id = data_id

    def __str__(self):
        return str(tuple(map(str, (self.index, self.data_id))))


class TableSelectAndEditAction(TableAction):
    action_name = None
    ActionDataCls = TableSelectAndEditActionData

    def __init__(self, *args):
        super(TableSelectAndEditAction, self).__init__(*args)

        self.row = self.data.find_index(self.action_data.data_id)

    def _redo(self):
        return True

    def _undo(self):
        pass


class TableSelectAndEditCommand(TableCommand):
    push_to_stack = False

    def __init__(self, *args):
        super(TableSelectAndEditCommand, self).__init__(*args)

        self.action = self.action
        """:type: TableSelectAndEditAction"""

    def redo(self):
        row = self.action.row
        column = self.action.action_data.index[1]

        self._dock.table1.select_and_edit((row, column))

        self._raise_dock()

        return True


########################################################################################################################

class TableRemoveActionData(TableActionData):
    def __str__(self):
        return str(tuple(map(str, (self.index,))))


class TableRemoveAction(TableAction):
    action_name = None
    ActionDataCls = TableRemoveActionData

    def __init__(self, *args):
        super(TableRemoveAction, self).__init__(*args)

        self.removed_data = None

    def _redo(self):

        index = self.action_data.index

        if not self.main_data.can_remove(self.data, index[0]):
            config.push_error("TableRemoveAction: can't remove index %d!" % index[0])
            return False

        self.removed_data = self.data.remove(index[0])

        if self.removed_data is None:
            return False

        return True

    def _undo(self):
        if self.removed_data is None:
            return

        self.data.insert(self.action_data.index[0], self.removed_data)


class TableRemoveCommand(TableCommand):
    def __init__(self, *args):
        super(TableRemoveCommand, self).__init__(*args)

    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()
        dock.table1.select(self.action.action_data.index)

        self._raise_dock()


########################################################################################################################

class TableInsertActionData(TableActionData):
    def __str__(self):
        return str(tuple(map(str, (self.index,))))


class TableInsertAction(TableAction):
    action_name = None
    ActionDataCls = TableInsertActionData

    def __init__(self, *args):
        super(TableInsertAction, self).__init__(*args)

        self.inserted_data = None

    def _redo(self):
        self.inserted_data = self.data.insert(self.action_data.index)

        if self.inserted_data is None:
            return False

        return True

    def _undo(self):
        if self.inserted_data is None:
            return

        self.data.remove(self.action_data.index)


class TableInsertCommand(TableCommand):
    def __init__(self, *args):
        super(TableInsertCommand, self).__init__(*args)

        self._removed = None

    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()
        dock.table1.select(self.action.action_data.index)

        self._raise_dock()


########################################################################################################################


class TableSetDataActionData(TableActionData):
    def __init__(self, index, new_data, *args, **kwargs):
        super(TableSetDataActionData, self).__init__(index, *args)

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
            raise ValueError('TableSetDataActionData: Key not recognized!')

    def __str__(self):
        return str(str(self.index), str(self.new_data))


class TableSetDataAction(TableAction):
    action_name = None
    ActionDataCls = TableSetDataActionData

    def __init__(self, *args):
        super(TableSetDataAction, self).__init__(*args)

        self.old_data = None

        self.state_diff = None

        self.is_valid = False

        self._validate()

    def _validate(self):
        self.is_valid = True

    def _redo(self):
        row, column = self.action_data.index

        self.old_data = self.data[row][column]
        old_state = self.data[row].get_state()

        self.data[row][column] = self.action_data.new_data

        new_state = self.data[row].get_state()

        state_diff = self.data[row].compare_states(old_state, new_state)
        self.state_diff = tuple([tmp[0] for tmp in state_diff])

        if self.state_diff:
            return True
        else:
            return False

    def _undo(self):
        if self.state_diff is None:
            return

        self.data[self.action_data.index[0]].set_state(self.state_diff)

    def _after_redo(self):
        if self.state_diff and self.action_data.index[1] == 0:
            self.main_data.rename_ids(self.data, self.old_data, self.action_data.new_data)

    def _after_undo(self):
        if self.state_diff and self.action_data.index[1] == 0:
            self.main_data.rename_ids(self.data, self.action_data.new_data, self.old_data)


class TableSetDataCommand(TableCommand):
    def __init__(self, *args):
        super(TableSetDataCommand, self).__init__(*args)

        self._count = 0

    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()

        if self._count == 0:
            offset = 1
        else:
            offset = 0

        self._count += 1

        row, column = self.action.action_data.index
        key_pressed = self.action.action_data.key_pressed

        max_row = dock.table1.row_count()
        max_col = dock.table1.colum_count()

        if key_pressed == 0:
            row += offset
        elif key_pressed == 1:
            column += offset

        if row >= max_row:
            row = max_row - 1

        if column >= max_col:
            column = max_col - 1

        dock.table1.select((row, column))

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


class TablePasteActionData(TableActionData):
    def __init__(self, index, selection, new_data, *args):
        super(TablePasteActionData, self).__init__(index, *args)

        self.selection = selection  # [(row1, col1), (row2, col2)]
        """:type: list[tuple[int]]"""

        self.new_data = new_data

    def __str__(self):
        return str(str(self.index), str(tuple(map(str, self.selection))), str(self.new_data))


class TablePasteAction(TableAction):
    action_name = None
    ActionDataCls = TablePasteActionData
    SetData = None

    def __init__(self, *args):
        super(TablePasteAction, self).__init__(*args)

        self._actions = []

        self.new_data = []

        self._validate()

    def _validate(self):
        (row1, col1), (row2, col2) = self.action_data.selection

        selected_row_count = row2 - row1 + 1
        selected_col_count = col2 - col1 + 1

        new_data = self.new_data = str_to_list(self.action_data.new_data)

        paste_rows = len(new_data)

        if paste_rows == 0:
            self.is_valid = False
            return

        paste_cols = len(new_data[0])

        if selected_row_count < paste_rows or selected_col_count < paste_cols:
            selected_row_count = paste_rows
            selected_col_count = paste_cols

        elif selected_row_count % paste_rows != 0 or selected_col_count % paste_cols != 0:
            selected_row_count = paste_rows
            selected_col_count = paste_cols

        row2 = row1 + selected_row_count - 1
        col2 = col1 + selected_col_count - 1

        table_rows = len(self.data)
        table_columns = len(self.data[0])

        if row2 >= table_rows or col2 >= table_columns:
            self.is_valid = False
            config.push_error('TablePasteAction: Cannot paste outside of range!')
            return

        repeat_rows = selected_row_count // paste_rows
        repeat_cols = selected_col_count // paste_cols

        a = np.array(self.new_data)

        b = np.concatenate([a] * repeat_rows)
        c = np.concatenate([b] * repeat_cols, axis=1)

        self.new_data = c.tolist()

        self.is_valid = True

    def _redo(self):

        if not self.new_data:
            self.is_valid = False
            return False

        # noinspection PyUnusedLocal
        (first_row, first_column), (last_row, last_column) = self.action_data.selection

        min_size = min(len(self.new_data), len(self.data))

        for i in range(min_size):
            row = first_row + i

            data_i = self.new_data[i]

            for j in range(len(data_i)):
                column = first_column + j

                data_ij = data_i[j]

                action_data = self.ActionDataCls((row, column), data_ij)
                action = self.SetData(self.main_data, action_data)
                self._actions.append(action)
                action.redo()

        return True

    def _undo(self):
        for action in reversed(self._actions):
            action.undo()

        self._actions = []


class TablePasteCommand(TableCommand):
    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()

        # noinspection PyUnusedLocal
        (first_row, first_column), (last_row, last_column) = self.action.action_data.selection

        dock.table1.select((first_row, first_column))

        self._raise_dock()


########################################################################################################################

class TableSetRowsActionData(TableActionData):
    def __init__(self, index, row_count, *args):
        super(TableSetRowsActionData, self).__init__(index, *args)

        self.row_count = row_count

    def __str__(self):
        return str(tuple(map(str, (self.index, self.row_count,))))


class TableSetRowsAction(TableAction):
    action_name = None
    ActionDataCls = TableSetRowsActionData
    Add = None
    Remove = None

    def __init__(self, *args):
        super(TableSetRowsAction, self).__init__(*args)

        self.old_row_count = len(self.data)

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

            for i in range(diff):
                action = self.Add(self.main_data)
                self._actions.append(action)
                self.action_success.append(action.redo())

        else:
            diff = self.old_row_count - new_row_count

            last_index = len(self.data) - 1

            for i in range(diff):
                action = self.Remove(self.main_data, last_index)
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


class TableSetRowsCommand(TableCommand):
    def __init__(self, *args):
        super(TableSetRowsCommand, self).__init__(*args)

        self._added = None
        self._removed = None

    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()

        self._raise_dock()


########################################################################################################################


class TableUpDownActionData(TableActionData):
    def __str__(self):
        return str(tuple(map(str, (self.index,))))


class TableUpDownAction(TableAction):
    action_name = None
    ActionDataCls = TableUpDownActionData
    offset = 0

    def __init__(self, *args):
        super(TableUpDownAction, self).__init__(*args)
        
        pass

    def _redo(self):
        current_row = self.action_data.index[0]    
        new_row = current_row + self.offset

        data = self.data

        if new_row < 0 or new_row >= len(data):
            return False

        data_index = data[current_row]
        data_index_m1 = data[new_row]

        data[current_row] = data_index_m1
        data[new_row] = data_index

        return True

    def _undo(self):
        current_row = self.action_data.index[0]    
        new_row = current_row + self.offset

        data = self.data

        data_index = data[current_row]
        data_index_m1 = data[new_row]

        data[current_row] = data_index_m1
        data[new_row] = data_index
        
    def new_row(self):
        current_row = self.action_data.index[0]    
        return current_row + self.offset
    
    def new_index(self):
        current_row = self.action_data.index[0]    
        return current_row + self.offset, self.action_data.index[1]


class TableUpAction(TableUpDownAction):
    offset = -1


class TableDownAction(TableUpDownAction):
    offset = 1


class TableUpDownCommand(TableCommand):
    
    def __init__(self, *args):
        super(TableUpDownCommand, self).__init__(*args)
        
        self.action = self.action
        """:type: TableUpDownAction"""
    
    def _after_redo(self):
        dock = self._dock
        dock.table1.update_all()
        dock.table1.select(self.action.new_index())

        self._raise_dock()

    def _after_undo(self):
        dock = self._dock
        dock.table1.update_all()
        dock.table1.select(self.action.action_data.index)

        self._raise_dock()


class TableUpCommand(TableUpDownCommand):
    pass


class TableDownCommand(TableUpDownCommand):
    pass


########################################################################################################################


class TableRightClickActionData(TableActionData):
    def __str__(self):
        return str(tuple(map(str, (self.index,))))


class TableRightClickAction(TableAction):
    action_name = None
    ActionDataCls = TableRightClickActionData
    log_action = False

    def __init__(self, *args):
        super(TableRightClickAction, self).__init__(*args)

        self.validation_data = []

    def _redo(self):
        self.validation_data = self.main_data.validation_data(self.data, self.action_data.index)

        return True

    def _undo(self):
        pass


class TableRightClickCommand(TableCommand):
    push_to_stack = False
    set_data_action = None
    
    def __init__(self, *args):
        super(TableRightClickCommand, self).__init__(*args)
        
        self.action = self.action
        """:type: TableRightClickAction"""

    def _after_redo(self):
        success, (data, index) = validation_context_menu(self.action.validation_data)
        if success:
            index = self.action.action_data.index
            config.dispatcher.dispatch((self.set_data_action, TableSetDataActionData(index, str(data))))


########################################################################################################################


class TableActions(object):
    TableAddAction = TableAddAction
    TableDownAction = TableDownAction
    TableInsertAction = TableInsertAction
    TablePasteAction = TablePasteAction
    TableRemoveAction = TableRemoveAction
    TableRightClickAction = TableRightClickAction
    TableSelectAndEditAction = TableSelectAndEditAction
    TableSetDataAction = TableSetDataAction
    TableSetRowsAction = TableSetRowsAction
    TableUpAction = TableUpAction


class TableCommands(object):
    TableAddCommand = TableAddCommand
    TableDownCommand = TableDownCommand
    TableInsertCommand = TableInsertCommand
    TablePasteCommand = TablePasteCommand
    TableRemoveCommand = TableRemoveCommand
    TableRightClickCommand = TableRightClickCommand
    TableSelectAndEditCommand = TableSelectAndEditCommand
    TableSetDataCommand = TableSetDataCommand
    TableSetRowsCommand = TableSetRowsCommand
    TableUpCommand = TableUpCommand
