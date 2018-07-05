"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities.command_dispatcher import Action, Command, ActionData

import numpy as np
# import warnings

from qtpy import QtWidgets


########################################################################################################################

class BaseActionData(ActionData):
    def __init__(self, index):
        super(BaseActionData, self).__init__()
        self.index = index

    def __str__(self):
        return '(%d,)' % self.index


# noinspection PyAbstractClass
class BaseAction(Action):
    def __init__(self, main_data, action_data):
        super(BaseAction, self).__init__(main_data, action_data)

        self.main_data = main_data
        """:type: fem.utilities.table_data_widget.model.MainData"""

        self.action_data = action_data
        """:type: BaseActionData"""


# noinspection PyAbstractClass
class BaseCommand(Command):
    def __init__(self, main_window, action):
        super(BaseCommand, self).__init__(main_window, action)

        self.main_window = main_window
        """:type: fem.utilities.table_data_widget.gui.TableDataWidget"""

        self.action = action
        """:type: AddAction"""

    def _before_redo(self):
        pass

    def _after_redo(self):
        self.main_window.update_all()

    def _before_undo(self):
        pass

    def _after_undo(self):
        self.main_window.update_all()


########################################################################################################################

class AddActionData(ActionData):
    def __init__(self, *args):
        super(AddActionData, self).__init__()

    def __str__(self):
        return '()'


class AddAction(BaseAction):
    ActionDataCls = AddActionData

    action_name = 'Add'

    def __init__(self, main_data, action_data):
        super(AddAction, self).__init__(main_data, action_data)

    def _before_redo(self):
        pass

    def _redo(self):
        self.main_data.add()
        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.delete(len(self.main_data) - 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class AddCommand(BaseCommand):
    command_name = 'Add'

    def _after_redo(self):
        super(AddCommand, self)._after_redo()
        self.main_window.tableView_list.select_last_row()

    def _after_undo(self):
        super(AddCommand, self)._after_undo()
        self.main_window.tableView_list.select_last_row()


########################################################################################################################

class RemoveActionData(BaseActionData):
    pass


class RemoveAction(BaseAction):
    ActionDataCls = RemoveActionData

    action_name = 'Remove'

    def __init__(self, main_data, action_data):
        super(RemoveAction, self).__init__(main_data, action_data)

        self._removed_data = None
        self._removed_key = None

    def _before_redo(self):
        pass

    def _redo(self):
        try:
            self._removed_key = self.main_data.data_keys[self.action_data.index]
        except IndexError:
            return False

        self._removed_data = self.main_data.data[self._removed_key]
        self.main_data.delete(self.action_data.index)
        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.insert(self.action_data.index, self._removed_key, self._removed_data)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class RemoveCommand(BaseCommand):
    command_name = 'Remove'

    def _after_redo(self):
        super(RemoveCommand, self)._after_redo()

        index = self.action.action_data.index

        if index >= len(self.action.main_data):
            index -= 1

        self.main_window.tableView_list.set_selection([[index, 0]])

    def _after_undo(self):
        super(RemoveCommand, self)._after_undo()
        self.main_window.tableView_list.set_selection([[self.action.action_data.index, 0]])


########################################################################################################################

class InsertActionData(BaseActionData):
    pass


class InsertAction(BaseAction):
    ActionDataCls = InsertActionData

    action_name = 'Insert'

    def __init__(self, main_data, action_data):
        super(InsertAction, self).__init__(main_data, action_data)

    def _before_redo(self):
        pass

    def _redo(self):
        self.main_data.insert(self.action_data.index)
        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.delete(self.action_data.index)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class InsertCommand(BaseCommand):
    command_name = 'Insert'

    def _after_redo(self):
        super(InsertCommand, self)._after_redo()
        self.main_window.tableView_list.set_selection([[self.action.action_data.index, 0]])

    def _after_undo(self):
        super(InsertCommand, self)._after_undo()
        self.main_window.tableView_list.set_selection([[self.action.action_data.index, 0]])


########################################################################################################################

class SetDataActionData(ActionData):
    def __init__(self, index, value):
        super(SetDataActionData, self).__init__()

        self.index = index
        self.value = value

    def __str__(self):
        return '(%s, %s)' % (str(self.index), str(self.value))


class SetDataAction(BaseAction):
    ActionDataCls = SetDataActionData

    action_name = 'SetData'

    def __init__(self, main_data, action_data):
        super(SetDataAction, self).__init__(main_data, action_data)

        self.main_data = main_data
        """:type: ..model._main_data.MainDataInterface1"""

        self.action_data = action_data
        """:type: SetDataActionData"""

        self.class_name = self.main_data.__class__.__name__

        self.old_value = self.main_data.get_data(self.action_data.index)

        self.offset = 1

    def _before_redo(self):
        pass

    def _redo(self):
        return self.main_data.set_data(self.action_data.index, self.action_data.value)

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.set_data(self.action_data.index, self.old_value)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class SetDataCommand(BaseCommand):
    command_name = 'SetData'

    def __init__(self, main_window, action):
        super(SetDataCommand, self).__init__(main_window, action)

        if action.class_name == 'MainDataInterface1':
            self.table = self.main_window.tableView_list
        else:
            self.table = self.main_window.tableView_data

    def _after_redo(self):
        super(SetDataCommand, self)._after_redo()

        index = list(self.action.action_data.index)

        if self.action.class_name == 'MainDataInterface2':
            index[0] += self.action.offset

        self.table.set_selection_and_index([[index[0], index[1]]])

        self.action.offset = 0

    def _after_undo(self):
        super(SetDataCommand, self)._after_undo()
        index = self.action.action_data.index
        self.table.set_selection_and_index([[index[0], index[1]]])


########################################################################################################################

class UpActionData(BaseActionData):
    pass


class UpAction(BaseAction):
    ActionDataCls = UpActionData

    action_name = 'Up'

    def __init__(self, main_data, action_data):
        super(UpAction, self).__init__(main_data, action_data)

        self.main_data = main_data
        """:type: ..model.MainData"""

        self.action_data = action_data
        """:type: BaseActionData"""

    def _before_redo(self):
        pass

    def _redo(self):
        return self.main_data.up(self.action_data.index)

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.down(self.action_data.index - 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class UpCommand(BaseCommand):
    command_name = 'Up'

    def _after_redo(self):
        super(UpCommand, self)._after_redo()
        self.main_window.tableView_list.set_selection([[self.action.action_data.index - 1, 0]])

    def _after_undo(self):
        super(UpCommand, self)._after_undo()
        self.main_window.tableView_list.set_selection([[self.action.action_data.index, 0]])


########################################################################################################################

class DownActionData(BaseActionData):
    pass


class DownAction(BaseAction):
    ActionDataCls = DownActionData

    action_name = 'Down'

    def __init__(self, main_data, action_data):
        super(DownAction, self).__init__(main_data, action_data)

        self.main_data = main_data
        """:type: ..model.MainData"""

        self.action_data = action_data
        """:type: BaseActionData"""

    def _before_redo(self):
        pass

    def _redo(self):
        return self.main_data.down(self.action_data.index)

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.up(self.action_data.index + 1)

    def _after_undo(self):
        pass

    def _validate(self):
        self.is_valid = True


class DownCommand(BaseCommand):
    command_name = 'Down'

    def _after_redo(self):
        super(DownCommand, self)._after_redo()
        self.main_window.tableView_list.set_selection([[self.action.action_data.index + 1, 0]])

    def _after_undo(self):
        super(DownCommand, self)._after_undo()
        self.main_window.tableView_list.set_selection([[self.action.action_data.index, 0]])


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
    def __init__(self, selection, data):
        super(PasteActionData, self).__init__()

        self.selection = selection
        self.data = data

    def __str__(self):
        return '(%s, %s)' % (str(self.selection), str(self.data))


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences
class PasteAction(BaseAction):
    """
    Action for pasting _data_roles into table_2.
    """

    ActionDataCls = PasteActionData
    action_name = 'Paste'

    def __init__(self, main_data, action_data):
        super(PasteAction, self).__init__(main_data, action_data)

        self.main_data = main_data
        """:type: ..model._main_data.MainDataInterface1"""

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
        self.new_data = str_to_list(self.action_data.data)

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

        table_rows, table_columns = self.main_data.shape()

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

        min_size = min(len(self.new_data), len(self.main_data))

        self.paste_indices = []

        for i in range(min_size):
            row = first_row + i

            data_i = self.new_data[i]

            for j in range(len(data_i)):
                column = first_column + j

                action_data = SetDataActionData((row, column), data_i[j])
                action = SetDataAction(self.main_data, action_data)

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

    def __init__(self, main_window, action, table):
        super(PasteCommand, self).__init__(main_window, action)

        self.table = table

    def _before_redo(self):
        pass

    def _after_redo(self):
        self.table.update_all()
        self.table.set_selection(self.action.paste_indices)

    def _before_undo(self):
        pass

    def _after_undo(self):
        self.table.update_all()
        self.table.set_selection(self.action.paste_indices)


########################################################################################################################


class ImportActionData(ActionData):
    def __init__(self, filename, options=None):
        super(ImportActionData, self).__init__()

        self.filename = filename
        self.options = options

    def __str__(self):
        if self.options is None:
            return '(%s,)' % self.filename
        else:
            return '(%s, %s)' % (self.filename, str(self.options))


class ImportAction(BaseAction):

    ActionDataCls = ImportActionData
    action_name = 'Import'

    def __init__(self, main_data, action_data, config):
        super(ImportAction, self).__init__(main_data, action_data)

        self.config = config

        from ..gui import DataImport

        data_import = DataImport(self.main_data, config)
        data_import.read_file(self.action_data.filename)

        data_import.show()

        app = QtWidgets.QApplication.instance()

        while data_import.isVisible():
            app.processEvents()

        if not data_import.accepted:
            self.is_valid = False
            return

        # if self.action_data.options is not None:
        #     data_import.set_options(self.action_data.options)

        self.data = data_import.get_data()
        self.old_data = self.main_data.serialize()

        self._validate()

    def _validate(self):

        for i in range(len(self.data)):
            try:
                tmp = [list(map(float, lst)) for lst in self.data[i][1]]
                tmp = b''.join([np.array(tmp_, dtype=np.float64).tostring() for tmp_ in tmp])
                tmp = np.fromstring(tmp, dtype=np.float64)

                cols = self.main_data.columns()

                tmp = np.array(tmp.reshape((cols, tmp.size // cols)))
                tmp = np.transpose(tmp)
                tmp = tmp.reshape((tmp.size // cols, cols))

                self.data[i][1] = tmp.tostring()

            except Exception:
                self.config.push_error(
                    'Import: unable to convert _data_roles to floating point during importing for %s!' % self.data[i][0]
                )
                self.is_valid = False
                return

        self.is_valid = True

    def _before_redo(self):
        pass

    def _redo(self):
        self.main_data.load(self.data)
        return True

    def _after_redo(self):
        pass

    def _before_undo(self):
        pass

    def _undo(self):
        self.main_data.clear()
        self.main_data.load(self.old_data)

    def _after_undo(self):
        pass


class ImportCommand(BaseCommand):
    command_name = 'Import'

    def _after_redo(self):
        self.main_window.update_all()

    def _after_undo(self):
        self.main_window.update_all()


########################################################################################################################

class Actions(object):
    AddAction = AddAction
    RemoveAction = RemoveAction
    InsertAction = InsertAction
    SetDataAction = SetDataAction
    UpAction = UpAction
    DownAction = DownAction
    PasteAction = PasteAction
    ImportAction = ImportAction

    @classmethod
    def attach(cls, dispatcher):

        def _attach(cls_):
            dispatcher(cls_.action_name)(cls_)

        _attach(cls.AddAction)
        _attach(cls.RemoveAction)
        _attach(cls.InsertAction)
        _attach(cls.SetDataAction)
        _attach(cls.UpAction)
        _attach(cls.DownAction)
        _attach(cls.PasteAction)
        _attach(cls.ImportAction)


class Commands(object):
    AddCommand = AddCommand
    RemoveCommand = RemoveCommand
    InsertCommand = InsertCommand
    SetDataCommand = SetDataCommand
    UpCommand = UpCommand
    DownCommand = DownCommand
    PasteCommand = PasteCommand
    ImportCommand = ImportCommand

    @classmethod
    def attach(cls, dispatcher):

        def _attach(cls_):
            dispatcher(cls_.command_name)(cls_)

        _attach(cls.AddCommand)
        _attach(cls.RemoveCommand)
        _attach(cls.InsertCommand)
        _attach(cls.SetDataCommand)
        _attach(cls.UpCommand)
        _attach(cls.DownCommand)
        _attach(cls.PasteCommand)
        _attach(cls.ImportCommand)
