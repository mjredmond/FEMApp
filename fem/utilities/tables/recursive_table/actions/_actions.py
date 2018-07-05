"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities.command_dispatcher import Action, Command, ActionData, dispatcher_version
from fem.utilities.debug import debuginfo

import numpy as np
# import warnings

from qtpy import QtWidgets

from ast import literal_eval

assert dispatcher_version == '4'

# FIXME: all references should be WEAK references to prevent reference cycles, possible problem with garbage collecting


########################################################################################################################

class BaseActionData(ActionData):
    def __init__(self, index):
        super(BaseActionData, self).__init__()
        self.index = index

    def __str__(self):
        return '(%s,)' % str(self.index)

    def split(self):
        return None, str(self.index)


# noinspection PyAbstractClass
class BaseAction(Action):
    main_data = None
    """:type: fem.utilities.tables.basic_table.model.MainData"""

    def __init__(self, action_data):
        super(BaseAction, self).__init__(action_data)

        self.table_data = self.main_data

        self.action_data = action_data
        """:type: BaseActionData"""

    @property
    def table_data(self):
        return self.main_data

    @table_data.setter
    def table_data(self, value):
        self.main_data = value


# noinspection PyAbstractClass
class BaseCommand(Command):
    main_window = None
    """:type: fem.utilities.tables.basic_table.gui.RecursiveTable"""

    def __init__(self, action, **kwargs):
        super(BaseCommand, self).__init__(action, **kwargs)

        self.recursive_table = self.main_window

        self.table = self.recursive_table.table
        """:type: fem.utilities.tables.empty_table.EmptyTable"""

        self.action = action
        """:type: BaseAction"""

        self.current_index = self.table.current_index()

        # self.selection = self.table.selection()

    @property
    def recursive_table(self):
        """

        :return: fem.utilities.tables.recursive_table.RecursiveTable
        """
        return self.main_window

    @recursive_table.setter
    def recursive_table(self, value):
        self.main_window = value

    def _before_redo(self):
        if self.recursive_table.get_model is not self.action.table_data:
            self.action.table_data = self.recursive_table.get_model

    def _after_redo(self):
        self.table.set_selection([self.current_index])
        self.recursive_table.update_all()
        self.table.setFocus()

    def _before_undo(self):
        pass

    def _after_undo(self):
        self.table.set_selection([self.current_index])
        self.recursive_table.update_all()
        self.table.setFocus()


########################################################################################################################

class AddActionData(ActionData):
    def __init__(self, *args):
        super(AddActionData, self).__init__()

    def __str__(self):
        return '()'

    def split(self):
        return None, None


class AddAction(BaseAction):
    ActionDataCls = AddActionData

    action_name = 'Add'

    def __init__(self, action_data):
        super(AddAction, self).__init__(action_data)

        self._removed_data = None

    def _before_redo(self):
        pass

    def _redo(self):

        if self._removed_data is not None:
            self.table_data.add(self._removed_data)
        else:
            self._removed_data = self.table_data.add()

        if self._removed_data is None:
            return False

        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.table_data.remove(len(self.table_data) - 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class AddCommand(BaseCommand):
    command_name = 'Add'

    def _after_redo(self):
        super(AddCommand, self)._after_redo()
        col = self.current_index[1]
        row = self.table.row_count() - 1

        if col == -1:
            col = 0

        # debuginfo('set selection', (row, col))

        self.table.set_selection_and_index([[row, col]])

    def _after_undo(self):
        super(AddCommand, self)._after_undo()
        col = self.current_index[1]
        row = self.table.row_count() - 1

        if col == -1:
            col = 0

        self.table.set_selection_and_index([[row, col]])


########################################################################################################################

class RemoveActionData(ActionData):
    def __init__(self, selection):
        super(RemoveActionData, self).__init__()
        self.selection = selection

    def __str__(self):
        return '(%s,)' % str(self.selection)

    def split(self):
        return None, str(self.selection)


class RemoveAction(BaseAction):
    ActionDataCls = RemoveActionData

    action_name = 'Remove'

    def __init__(self, action_data):
        super(RemoveAction, self).__init__(action_data)

        self._removed_data = []
        self._removed_indices = []
        self._removed_id = None

    def _before_redo(self):
        pass

    def _redo(self):
        self._removed_data = []
        self._removed_indices = []

        selection = list(reversed(self.action_data.selection))

        if len(selection) == 0:
            selection = [(len(self.table_data) - 1, 0)]
            self.action_data.selection = selection

        for index in selection:
            tmp = self.table_data.remove(index[0])

            if tmp is None:
                continue

            if len(tmp) > 0:

                _data = tmp[0]

                if _data is None:
                    continue

                self._removed_data.append(_data)
                self._removed_indices.append(index)

        if len(self._removed_data) == 0:
            return False

        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        removed_data = list(reversed(self._removed_data))
        removed_indices = list(reversed(self._removed_indices))

        for i in range(len(removed_indices)):
            index = removed_indices[i]
            self.table_data.insert(index[0])
            self.table_data[index[0]].load(removed_data[i])

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class RemoveCommand(BaseCommand):
    command_name = 'Remove'

    def _after_redo(self):
        super(RemoveCommand, self)._after_redo()

        if len(self.action.action_data.selection) == 1:
            index = list(self.action.action_data.selection[0])
            if index[0] >= len(self.action.main_data):
                index[0] = len(self.action.main_data) - 1

            self.table.set_selection_and_index((index,))

        else:
            self.table.set_selection_and_index((self.action.action_data.selection[0],))

    def _after_undo(self):
        super(RemoveCommand, self)._after_undo()
        self.table.set_selection_and_index(self.action.action_data.selection)


########################################################################################################################

class InsertActionData(BaseActionData):
    pass


class InsertAction(BaseAction):
    ActionDataCls = InsertActionData

    action_name = 'Insert'

    def __init__(self, action_data):
        super(InsertAction, self).__init__(action_data)

    def _before_redo(self):
        pass

    def _redo(self):
        if self.table_data.insert(self.action_data.index[0]) is None:
            return False

        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.table_data.remove(self.action_data.index[0])

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class InsertCommand(BaseCommand):
    command_name = 'Insert'

    def _after_redo(self):
        super(InsertCommand, self)._after_redo()
        index = self.action.action_data.index
        self.table.set_selection([[index[0], index[1]]])

    def _after_undo(self):
        super(InsertCommand, self)._after_undo()
        index = self.action.action_data.index

        if index[0] >= self.table.table.model().rowCount():
            index[0] -= 1

        self.table.set_selection([[index[0], index[1]]])


########################################################################################################################

class SetDataActionData(ActionData):
    def __init__(self, index, value, enter_down=None):
        super(SetDataActionData, self).__init__()

        self.index = index

        if isinstance(value, str) and ',' in value:
            tmp = value.replace('[', '').replace(']', '').replace('<', '').replace('>', '').replace(' ', '')
            self.value = tmp.split(',')
        else:
            self.value = value

        try:
            self.value = literal_eval(str(self.value))
        except (TypeError, ValueError, SyntaxError):
            self.value = str(self.value)

        self.enter_down = enter_down

    def __str__(self):
        if isinstance(self.value, str):
            return "(%s, '%s')" % (str(self.index), self.value)

        return '(%s, %s)' % (str(self.index), str(self.value))

    def split(self):
        return str(self.index), str((self.value,))


class SetDataAction(BaseAction):
    ActionDataCls = SetDataActionData

    action_name = 'SetData'

    def __init__(self, action_data):
        super(SetDataAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: SetDataActionData"""

        data = self.table_data[self.action_data.index[0]]

        self.old_data = data.serialize()
        self.old_value = data[self.action_data.index[1]]

        if self.action_data.enter_down is True:
            self.offset = (1, 0)
        elif self.action_data.enter_down is False:
            self.offset = (0, 1)
        else:
            self.offset = (0, 0)

    def _before_redo(self):
        pass

    def _redo(self):
        result = self.table_data.set_data(self.action_data.index, self.action_data.value)
        return result[0]

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        # reset the value first, there may be global side effects
        # then reload all of the serialized applied_loads_data to undo local side effects
        self.table_data.set_data(self.action_data.index, self.old_value)
        self.table_data[self.action_data.index[0]].load(self.old_data)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class SetDataCommand(BaseCommand):
    command_name = 'SetData'

    def _after_redo(self):
        super(SetDataCommand, self)._after_redo()

        index = list(self.action.action_data.index)

        index[0] += self.action.offset[0]
        index[1] += self.action.offset[1]

        data_shape = self.action.main_data.shape()

        if index[0] >= data_shape[0]:
            index[0] = data_shape[0] - 1

        if index[1] >= data_shape[1]:
            index[1] = data_shape[1] - 1

        # debuginfo('BasicTable set selection and index')

        self.table.set_selection_and_index([[index[0], index[1]]])

        self.action.offset = (0, 0)

    def _after_undo(self):
        super(SetDataCommand, self)._after_undo()
        index = self.action.action_data.index
        self.table.set_selection_and_index([[index[0], index[1]]])


########################################################################################################################

class UpActionData(BaseActionData):
    def split(self):
        return str(self.index), None


class UpAction(BaseAction):
    ActionDataCls = UpActionData

    action_name = 'Up'

    def __init__(self, action_data):
        super(UpAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: BaseActionData"""

    def _before_redo(self):
        pass

    def _redo(self):
        return self.table_data.up(self.action_data.index[0])

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.table_data.down(self.action_data.index[0] - 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class UpCommand(BaseCommand):
    command_name = 'Up'

    def _after_redo(self):
        super(UpCommand, self)._after_redo()
        index = self.action.action_data.index
        self.table.set_selection_and_index([[index[0] - 1, index[1]]])

    def _after_undo(self):
        super(UpCommand, self)._after_undo()
        index = self.action.action_data.index
        self.table.set_selection_and_index([[index[0], index[1]]])


########################################################################################################################

class DownActionData(BaseActionData):
    def split(self):
        return str(self.index), None


class DownAction(BaseAction):
    ActionDataCls = DownActionData

    action_name = 'Down'

    def __init__(self, action_data):
        super(DownAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: BaseActionData"""

    def _before_redo(self):
        pass

    def _redo(self):
        return self.table_data.down(self.action_data.index[0])

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.table_data.up(self.action_data.index[0] + 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class DownCommand(BaseCommand):
    command_name = 'Down'

    def _after_redo(self):
        super(DownCommand, self)._after_redo()
        index = self.action.action_data.index
        self.table.set_selection_and_index([[index[0] + 1, index[1]]])

    def _after_undo(self):
        super(DownCommand, self)._after_undo()
        index = self.action.action_data.index
        self.table.set_selection_and_index([[index[0], index[1]]])


########################################################################################################################

def str_to_list(data):
    """
    Converts a string delimited by \n and \t to a list of lists.
    :param data:
    :type data: str
    :return:
    :rtype: List[List[str]]
    """

    if isinstance(data, list):
        return data

    data = data.replace("'", '')

    try:
        if data[-1] == '\n':
            data = data[:-1]
    except IndexError:
        return

    tmp = data.split('\n')

    result = []

    for tmp_ in tmp:
        result.append(tmp_.split('\t'))

    return result


class PasteActionData(ActionData):
    def __init__(self, selection, data):
        super(PasteActionData, self).__init__()

        self.selection = selection
        self.data = str_to_list(data)

    def __str__(self):
        return '(%s, %s)' % (str(self.selection), str(self.data))

    def split(self):
        return None, str((self.selection, self.data))


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences
class PasteAction(BaseAction):
    """
    Action for pasting _data_roles into table_2.
    """

    ActionDataCls = PasteActionData
    action_name = 'Paste'

    SetDataAction = SetDataAction

    def __init__(self, action_data):
        super(PasteAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: PasteActionData"""

        self.new_data = []

        self.paste_indices = []

        self._actions = []

        self._validate()

    def _validate(self):
        selection = self.action_data.selection

        (row1, col1), (row2, col2) = selection

        selected_row_count = row2 - row1 + 1
        selected_col_count = col2 - col1 + 1

        # noinspection PyTypeChecker
        self.new_data = self.action_data.data

        if self.new_data is None:
            return

        # noinspection PyTypeChecker
        paste_rows = len(self.new_data)

        if paste_rows == 0:
            self.is_valid = False
            return

        paste_cols = len(self.new_data[0])

        # noinspection PyMissingOrEmptyDocstring
        def get_selection(selected, paste):
            if selected < paste:
                selected = paste

            if selected > paste:
                max_ = selected
                min_ = paste
            else:
                max_ = paste
                min_ = selected

            if max_ % min_ == 0:
                return max_
            else:
                return min_

        selected_row_count = get_selection(selected_row_count, paste_rows)
        selected_col_count = get_selection(selected_col_count, paste_cols)

        row2 = row1 + selected_row_count - 1
        col2 = col1 + selected_col_count - 1

        table_rows, table_columns = self.table_data.shape()

        if row2 >= table_rows or col2 >= table_columns:
            self.is_valid = False
            # TODO: add config
            # warnings.warn('Cannot paste outside of range!')
            # config.push_error('Cannot paste outside of range!')
            return

        repeat_rows = selected_row_count // paste_rows
        repeat_cols = selected_col_count // paste_cols

        a = np.array(self.new_data)

        b = np.concatenate([a] * repeat_rows)
        c = np.concatenate([b] * repeat_cols, axis=1)

        self.new_data = c.tolist()

        self.is_valid = True

    def _before_redo(self):
        pass

    def _redo(self):

        if not self.new_data:
            self.is_valid = False
            return False

        # noinspection PyUnusedLocal
        (first_row, first_column), (last_row, last_column) = self.action_data.selection

        min_size = min(len(self.new_data), len(self.table_data))

        self.paste_indices = []

        SetDataAction = self.SetDataAction

        for i in range(min_size):
            row = first_row + i

            data_i = self.new_data[i]

            for j in range(len(data_i)):
                column = first_column + j

                action_data = SetDataActionData((row, column), data_i[j])
                action = SetDataAction(action_data)

                action.main_data = self.table_data

                self._actions.append(action)

                action.redo()

                self.paste_indices.append([row, column])

        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        for action in reversed(self._actions):
            action.undo()

        self._actions = []

    def _after_undo(self):
        pass


# noinspection PyUnresolvedReferences, PyMissingOrEmptyDocstring
class PasteCommand(BaseCommand):
    """
    Command for pasting _data_roles into table_2.
    """

    command_name = 'Paste'

    def _after_redo(self):
        self.table.update_all()
        self.table.set_selection(self.action.paste_indices)

    def _before_undo(self):
        pass

    def _after_undo(self):
        self.table.update_all()
        self.table.set_selection(self.action.paste_indices)


########################################################################################################################

class SetRowsActionData(ActionData):
    def __init__(self, rows, *args):
        super(SetRowsActionData, self).__init__(*args)

        self.rows = rows

    def __str__(self):
        return '(%d)' % self.rows

    def split(self):
        return None, str(self.rows)


class SetRowsAction(BaseAction):
    ActionDataCls = SetRowsActionData

    action_name = 'SetRows'

    def __init__(self, action_data):
        super(SetRowsAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: SetRowsActionData"""

        self._removed_data = None
        self._added_data = None

        self.current_rows = self.table_data.shape()[0]

        self._validate()

    def _validate(self):
        rows = self.action_data.rows

        current_rows = self.table_data.shape()[0]

        if rows == current_rows:
            self.is_valid = False
            return

        if rows < 0:
            self.is_valid = False
            return

        self.is_valid = True

    def _before_redo(self):
        pass

    def _redo(self):
        rows = self.action_data.rows

        current_rows = self.table_data.shape()[0]

        if rows == current_rows:
            return False

        if rows > current_rows:
            diff = rows - current_rows
            self._added_data = self.table_data.add_multiple(diff, self._added_data)

        else:
            diff = current_rows - rows
            self._removed_data = self.table_data.remove_multiple(diff)

        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        if self._added_data is not None:
            self.table_data.remove_multiple(len(self._added_data))
        elif self._removed_data is not None:
            self.table_data.add_multiple(len(self._removed_data), self._removed_data)

    def _after_undo(self):
        pass


class SetRowsCommand(BaseCommand):
    command_name = 'SetRows'

    def _after_redo(self):
        super(SetRowsCommand, self)._after_redo()
        # self.table.select_last_row()

    def _after_undo(self):
        super(SetRowsCommand, self)._after_undo()
        # self.table.select_last_row()


########################################################################################################################

class Actions(object):
    AddAction = AddAction
    RemoveAction = RemoveAction
    InsertAction = InsertAction
    SetDataAction = SetDataAction
    UpAction = UpAction
    DownAction = DownAction
    PasteAction = PasteAction
    SetRowsAction = SetRowsAction

    @classmethod
    def attach(cls, dispatcher):

        def _attach(cls_):
            dispatcher(cls_.action_name)(cls_)

        members = cls.get_members()

        for member in members:
            _attach(member)

    @classmethod
    def set_main_data(cls, main_data):
        members = cls.get_members()

        for member in members:
            member.get_model = main_data

    @classmethod
    def get_members(cls):

        tmp = []

        for attr in dir(cls):
            attr_ = getattr(cls, attr)
            try:
                if issubclass(attr_, Action):
                    tmp.append(attr_)
            except TypeError:
                pass

        return tmp

    @classmethod
    def copy_cls(cls):
        """

        :return: Actions
        :rtype: Actions
        """

        class Tmp_(cls):
            pass

        Tmp_.__name__ = cls.__name__

        members = cls.get_members()

        for tmp in members:
            class _Tmp(tmp):
                pass

            name = tmp.__name__

            _Tmp.__name__ = name

            setattr(Tmp_, name, _Tmp)

        Tmp_.PasteAction.SetDataAction = Tmp_.SetDataAction

        return Tmp_


class Commands(object):
    AddCommand = AddCommand
    RemoveCommand = RemoveCommand
    InsertCommand = InsertCommand
    SetDataCommand = SetDataCommand
    UpCommand = UpCommand
    DownCommand = DownCommand
    PasteCommand = PasteCommand
    SetRowsCommand = SetRowsCommand

    @classmethod
    def attach(cls, dispatcher):

        def _attach(cls_):
            dispatcher(cls_.command_name)(cls_)

        members = cls.get_members()

        for member in members:
            _attach(member)

    @classmethod
    def set_main_window(cls, mw):
        members = cls.get_members()

        for member in members:
            member.main_window = mw

    @classmethod
    def get_members(cls):

        tmp = []

        for attr in dir(cls):
            attr_ = getattr(cls, attr)
            try:
                if issubclass(attr_, Command):
                    tmp.append(attr_)
            except TypeError:
                pass

        return tmp

    @classmethod
    def copy_cls(cls):
        """

        :return: Commands
        :rtype: Commands
        """

        class Tmp_(cls):
            pass

        Tmp_.__name__ = cls.__name__

        members = cls.get_members()

        for tmp in members:
            class _Tmp(tmp):
                pass

            name = tmp.__name__

            _Tmp.__name__ = name

            setattr(Tmp_, name, _Tmp)

        return Tmp_


def get_actions():
    """

    :return: Actions
    :rtype: Actions
    """
    return Actions.copy_cls()


def get_commands():
    """

    :return: Commands
    :rtype: Commands
    """
    return Commands.copy_cls()
