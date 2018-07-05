"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities.command_dispatcher import Action, Command, ActionData, dispatcher_version

import numpy as np
# import warnings

from qtpy import QtWidgets

from ast import literal_eval


assert dispatcher_version == '4'


########################################################################################################################

class BaseActionData(ActionData):
    def __init__(self, index1, index2):
        super(BaseActionData, self).__init__()
        self.index1 = index1
        self.index2 = index2

    def __str__(self):
        return '(%s, %s)' % (str(self.index1), str(self.index2))


# noinspection PyAbstractClass
class BaseAction(Action):
    main_data = None

    def __init__(self, action_data):
        super(BaseAction, self).__init__(action_data)

        self.main_data = self.main_data
        """:type: fem.utilities.tables.basic_table.model.MainData"""

        self.action_data = action_data
        """:type: BaseActionData"""

        self.subdata = self.main_data.subdata(self.action_data.index1)
        """:type: fem.utilities.tables.table_data.TableDataList"""


# noinspection PyAbstractClass
class BaseCommand(Command):
    main_window = None

    def __init__(self, action):
        super(BaseCommand, self).__init__(action)

        self.main_window = self.main_window
        """:type: fem.utilities.tables.basic_table.gui.BasicTable"""

        self.table_1 = self.main_window.table_1
        self.table_2 = self.main_window.table_2

        self.action = action
        """:type: BaseAction"""

    def _before_redo(self):
        pass

    def _after_redo(self):
        index1 = self.action.action_data.index1
        self.table_1.set_selection_and_index([[index1[0], index1[1]]])

        self.main_window.update_all()
        self.main_window.setFocus()
        self.table_1.setFocus()
        self.table_2.setFocus()

        try:
            index2 = self.action.action_data.index2
        except AttributeError:
            index2 = None

        if index2 is not None:
            self.table_2.set_selection_and_index([[index2[0], index2[1]]])

    def _before_undo(self):
        pass

    def _after_undo(self):
        index1 = self.action.action_data.index1
        self.table_1.set_selection_and_index([[index1[0], index1[1]]])

        self.main_window.update_all()
        self.main_window.setFocus()
        self.table_1.setFocus()
        self.table_2.setFocus()

        try:
            index2 = self.action.action_data.index2
        except AttributeError:
            index2 = None

        if index2 is not None:
            self.table_2.set_selection_and_index([[index2[0], index2[1]]])


########################################################################################################################

class AddActionData(ActionData):
    def __init__(self, index1):
        super(AddActionData, self).__init__()

        self.index1 = index1

    def __str__(self):
        return '(%s)' % str(self.index1)


class AddAction(BaseAction):
    ActionDataCls = AddActionData

    action_name = 'Add_2'

    def __init__(self, action_data):
        super(AddAction, self).__init__(action_data)

        self._removed_data = None

    def _before_redo(self):
        pass

    def _redo(self):
        self._removed_data = self.subdata.add(self._removed_data)
        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.subdata.remove(len(self.subdata) - 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class AddCommand(BaseCommand):
    command_name = 'Add_2'

    def _after_redo(self):
        super(AddCommand, self)._after_redo()
        self.table_2.select_last_row()

    def _after_undo(self):
        super(AddCommand, self)._after_undo()
        self.table_2.select_last_row()


########################################################################################################################

class RemoveActionData(ActionData):
    def __init__(self, index1, selection, *args):
        super(RemoveActionData, self).__init__(*args)

        self.index1 = index1
        self.selection = selection

    def __str__(self):
        return '(%s, %s)' % (str(self.index1), str(self.selection))


class RemoveAction(BaseAction):
    ActionDataCls = RemoveActionData

    action_name = 'Remove_2'

    def __init__(self, action_data):
        super(RemoveAction, self).__init__(action_data)

        self._removed_data = []

    def _before_redo(self):
        pass

    def _redo(self):
        self._removed_data = []

        selection = list(reversed(self.action_data.selection))

        if len(selection) == 0:
            selection = [(len(self.subdata) - 1, 0)]
            self.action_data.selection = selection

        for index in selection:
            self._removed_data.append(self.subdata.remove(index[0]))

        if len(self._removed_data) == 0:
            return False

        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        selection = self.action_data.selection

        removed_data = list(reversed(self._removed_data))

        for i in range(len(selection)):
            index = selection[i]
            data = removed_data[i]

            self.subdata.insert(index[0], data)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class RemoveCommand(BaseCommand):
    command_name = 'Remove_2'

    def _after_redo(self):
        super(RemoveCommand, self)._after_redo()

        if len(self.action.action_data.selection) == 1:
            index = list(self.action.action_data.selection[0])
            if index[0] >= len(self.action.subdata):
                index[0] = len(self.action.subdata) - 1

            self.table_2.set_selection_and_index((index,))

        else:
            self.table_2.set_selection_and_index((self.action.action_data.selection[0],))

    def _after_undo(self):
        super(RemoveCommand, self)._after_undo()
        self.table_2.set_selection_and_index(self.action.action_data.selection)


########################################################################################################################

class InsertActionData(BaseActionData):
    pass


class InsertAction(BaseAction):
    ActionDataCls = InsertActionData

    action_name = 'Insert_2'

    def __init__(self, action_data):
        super(InsertAction, self).__init__(action_data)

        self._removed_data = None

    def _before_redo(self):
        pass

    def _redo(self):
        self._removed_data = self.subdata.insert(self.action_data.index2[0], self._removed_data)
        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.subdata.remove(self.action_data.index2[0])

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class InsertCommand(BaseCommand):
    command_name = 'Insert_2'

    # def _after_redo(self):
    #     super(InsertCommand, self)._after_redo()
    #     index = self.action.action_data.index2
    #     self.table_2.set_selection([[index[0], index[1]]])
    #
    # def _after_undo(self):
    #     super(InsertCommand, self)._after_undo()
    #     index = self.action.action_data.index2
    #     self.table_2.set_selection([[index[0], index[1]]])


########################################################################################################################

class SetDataActionData(ActionData):
    def __init__(self, index1, index2, value, enter_down):
        super(SetDataActionData, self).__init__()

        self.index1 = index1
        self.index2 = index2

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
            return "(%s, %s, '%s')" % (str(self.index1), str(self.index2), self.value)

        return '(%s, %s, %s)' % (str(self.index1), str(self.index2), str(self.value))


class SetDataAction(BaseAction):
    ActionDataCls = SetDataActionData

    action_name = 'SetData_2'

    def __init__(self, action_data):
        super(SetDataAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: SetDataActionData"""

        data = self.subdata[self.action_data.index2[0]]
        self.old_data = self.subdata[self.action_data.index2[0]].serialize()
        self.old_value = data[self.action_data.index2[1]]

        if self.action_data.enter_down:
            self.offset = (1, 0)
        else:
            self.offset = (0, 1)

    def _before_redo(self):
        pass

    def _redo(self):
        result = self.subdata.set_data(self.action_data.index2, self.action_data.value)
        return result[0]

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.subdata.set_data(self.action_data.index2, self.old_value)
        self.subdata[self.action_data.index2[0]].load(self.old_data)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class SetDataCommand(BaseCommand):
    command_name = 'SetData_2'

    def _after_redo(self):
        super(SetDataCommand, self)._after_redo()

        index = list(self.action.action_data.index2)

        index[0] += self.action.offset[0]
        index[1] += self.action.offset[1]

        data_shape = self.action.subdata.shape()

        if index[0] >= data_shape[0]:
            index[0] = data_shape[0] - 1

        if index[1] >= data_shape[1]:
            index[1] = data_shape[1] - 1

        self.table_2.set_selection_and_index([[index[0], index[1]]])

        self.action.offset = (0, 0)


########################################################################################################################

class UpActionData(BaseActionData):
    pass


class UpAction(BaseAction):
    ActionDataCls = UpActionData

    action_name = 'Up_2'

    def __init__(self, action_data):
        super(UpAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: BaseActionData"""

    def _before_redo(self):
        pass

    def _redo(self):
        return self.subdata.up(self.action_data.index2[0])

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.subdata.down(self.action_data.index2[0] - 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class UpCommand(BaseCommand):
    command_name = 'Up_2'

    def _after_redo(self):
        super(UpCommand, self)._after_redo()
        index = self.action.action_data.index2
        self.table_2.set_selection_and_index([[index[0] - 1, index[1]]])

    def _after_undo(self):
        super(UpCommand, self)._after_undo()
        index = self.action.action_data.index2
        self.table_2.set_selection_and_index([[index[0], index[1]]])


########################################################################################################################

class DownActionData(BaseActionData):
    pass


class DownAction(BaseAction):
    ActionDataCls = DownActionData

    action_name = 'Down_2'

    def __init__(self, action_data):
        super(DownAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: BaseActionData"""

    def _before_redo(self):
        pass

    def _redo(self):
        return self.subdata.down(self.action_data.index2[0])

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.subdata.up(self.action_data.index2[0] + 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class DownCommand(BaseCommand):
    command_name = 'Down_2'

    def _after_redo(self):
        super(DownCommand, self)._after_redo()
        index = self.action.action_data.index2
        self.table_2.set_selection_and_index([[index[0] + 1, index[1]]])

    def _after_undo(self):
        super(DownCommand, self)._after_undo()
        index = self.action.action_data.index2
        self.table_2.set_selection_and_index([[index[0], index[1]]])


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
    def __init__(self, index1, selection, data):
        super(PasteActionData, self).__init__()

        self.index1 = index1
        self.selection = selection
        self.data = str_to_list(data)

    def __str__(self):
        return '(%s, %s, %s)' % (str(self.index1), str(self.selection), str(self.data))


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences
class PasteAction(BaseAction):
    """
    Action for pasting _data_roles into table_2.
    """

    ActionDataCls = PasteActionData
    action_name = 'Paste_2'

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

        table_rows, table_columns = self.subdata.shape()

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

        min_size = min(len(self.new_data), len(self.subdata))

        self.paste_indices = []

        index1 = self.action_data.index1

        SetDataAction = self.SetDataAction

        for i in range(min_size):
            row = first_row + i

            data_i = self.new_data[i]

            for j in range(len(data_i)):
                column = first_column + j

                action_data = SetDataActionData(index1, (row, column), data_i[j], False)
                action = SetDataAction(action_data)

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

    command_name = 'Paste_2'

    def _before_redo(self):
        pass

    def _after_redo(self):
        self.table_2.update_all()
        self.table_2.set_selection(self.action.paste_indices)

    def _before_undo(self):
        pass

    def _after_undo(self):
        self.table_2.update_all()
        self.table_2.set_selection(self.action.paste_indices)


########################################################################################################################

class SetRowsActionData(ActionData):
    def __init__(self, index1, rows, *args):
        super(SetRowsActionData, self).__init__(*args)

        self.index1 = index1
        self.rows = rows

    def __str__(self):
        return '(%s, %d)' % (str(self.index1), self.rows)


class SetRowsAction(BaseAction):
    ActionDataCls = SetRowsActionData

    action_name = 'SetRows_2'

    def __init__(self, action_data):
        super(SetRowsAction, self).__init__(action_data)

        self.action_data = action_data
        """:type: SetRowsActionData"""

        self._removed_data = None
        self._added_data = None

        self.current_rows = self.main_data.shape()[0]

        self._validate()

    def _validate(self):
        rows = self.action_data.rows

        current_rows = self.subdata.shape()[0]

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

        current_rows = self.subdata.shape()[0]

        if rows == current_rows:
            return False

        if rows > current_rows:
            diff = rows - current_rows
            self._added_data = self.subdata.add_multiple(diff, self._added_data)

        else:
            diff = current_rows - rows
            self._removed_data = self.subdata.remove_multiple(diff)

        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        if self._added_data is not None:
            self.subdata.remove_multiple(len(self._added_data))
        elif self._removed_data is not None:
            self.subdata.add_multiple(len(self._removed_data), self._removed_data)

    def _after_undo(self):
        pass


class SetRowsCommand(BaseCommand):
    command_name = 'SetRows_2'

    def _after_redo(self):
        super(SetRowsCommand, self)._after_redo()
        # self.table_2.set_selection([[self.action.current_rows, 0]])

    def _after_undo(self):
        super(SetRowsCommand, self)._after_undo()
        # self.table_2.select_last_row()


########################################################################################################################

class Actions2(object):
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

        :return: Actions2
        :rtype: Actions2
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


class Commands2(object):
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

        :return: Commands2
        :rtype: Commands2
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


def get_actions_2():
    """

    :return: Actions2
    :rtype: Actions2
    """
    return Actions2.copy_cls()


def get_commands_2():
    """

    :return: Commands2
    :rtype: Commands2
    """
    return Commands2.copy_cls()
