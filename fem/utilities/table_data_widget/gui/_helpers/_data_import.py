"""
package.module

description

author: Michael Redmond

"""

from qtpy import QtGui, QtWidgets, QtCore
import numpy as np


from .data_import_ui import Ui_Form

import itertools
from six import iteritems


def unique_name(name, names):
    if name not in names:
        return name

    suffix = 1

    name_ = '%s (%d)' % (name, suffix)

    while name_ in names:
        suffix += 1
        name_ = '%s (%d)' % (name, suffix)

    return name_


def transpose(a_):
    return list(map(list, itertools.zip_longest(*a_, fillvalue=0.)))


enabled = QtCore.Qt.ItemIsEnabled
editable = QtCore.Qt.ItemIsEditable
enabled_editable = enabled | editable
no_flags = QtCore.Qt.NoItemFlags


class _TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        super(_TableModel, self).__init__(parent)

        self._data = None
        self._existing_ids = None
        self._flags = None

        self.check_states = None
        """:type: np.ndarray"""

        self.header = parent.horizontalHeader()
        """:type: QtWidgets.QHeaderView"""

        self._header_clicks = [False, True, True, False]

        self.header.sectionClicked.connect(self._header_clicked)

    def _header_clicked(self, section):

        if section == 0:
            return

        tmp = self._header_clicks[section] = not self._header_clicks[section]

        for i in range(len(self.check_states)):
            if self._flags[i, section] & enabled:
                if section == 1:
                    self.check_states[i][section - 1] = tmp
                elif section == 2:
                    self.check_states[i][1] = tmp
                    self.check_states[i][2] = not tmp
                elif section == 3:
                    self.check_states[i][1] = not tmp
                    self.check_states[i][2] = tmp

        self.update_all()

    def set_data(self, data, existing_ids):
        self._data = data
        self._existing_ids = existing_ids

        self.check_states = np.array([[True, True, False]] * len(self._data), dtype=np.bool)

        self._flags = np.array([[enabled, enabled, enabled, enabled]] * len(self._data), dtype=object)

        for i in range(len(self._data)):

            lds = self._data[i]

            id = lds[0]
            load_size = self._existing_ids.get(id, 0)

            if len(lds[1][0]) >= load_size:
                self._flags[i, 1] = enabled
                self._flags[i, 2] = enabled
                self._flags[i, 3] = enabled
            else:
                self._flags[i, 1] = enabled
                self._flags[i, 2] = no_flags
                self._flags[i, 3] = no_flags
                self.check_states[i, 1] = False
                self.check_states[i, 2] = True

        self.parent().resizeColumnsToContents()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, col = index.row(), index.column()

        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self._data[row][0]

            elif col in (1, 2, 3):
                return self.check_states[row, col - 1]

            elif col == 4:
                if self._flags[row, 3] == no_flags:
                    return 'Cannot overwrite existing _data_roles because there are not enough loadcases.'
                else:
                    return ''

        return None

    def flags(self, index):
        row, col = index.row(), index.column()

        try:
            return self._flags[row, col]
        except IndexError:
            pass

        return super(_TableModel, self).flags(index)

    def rowCount(self, parent=None, *args, **kwargs):
        if self._data is None:
            return 0

        return len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        if self._data is None:
            return 0

        return 5

    def headerData(self, section, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return 'Detail ID'
            elif section == 1:
                return 'Import'
            elif section == 2:
                return 'Overwrite Existing Data'
            elif section == 3:
                return 'Rename Detail ID'
            elif section == 4:
                return 'Message'

        return super(_TableModel, self).headerData(section, orientation, role)

    def toggle(self, index):
        row, col = index.row(), index.column()

        if col == 0:
            return

        tmp = self.check_states[row, col - 1]

        if self._flags[row, col] & enabled:
            self.check_states[row, col - 1] = not tmp

            if col == 2:
                self.check_states[row, 2] = tmp
            elif col == 3:
                self.check_states[row, 1] = tmp

        self.update_all()

    def update_all(self):
        self.layoutChanged.emit()
        top_left = self.index(0, 0)
        bot_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bot_right)

    def get_data(self):
        ids = list(self._existing_ids.keys())

        _data = []

        for i in range(len(self._data)):

            if not self.check_states[i][0]:
                continue

            _id = self._data[i][0]

            if self.check_states[i][2]:
                _id = unique_name(_id, ids)
                ids.append(_id)

            _data.append([_id, self._data[i][1]])

        return _data

    def get_options(self):
        options = []

        for i in range(len(self._data)):

            if not self.check_states[i][0]:
                continue

            id = self._data[i][0]
            overwrite = self.check_states[i][1]

            options.append([id, overwrite])

        return options

    def set_options(self, options):
        keys = {}

        self.check_states = np.array([[False, False, False]] * len(self._data), dtype=np.bool)

        for i in range(len(self._data)):
            keys[self._data[i][0]] = i

        for option in options:
            _id, overwrite = option
            index = keys[_id]
            self.check_states[index, 0] = True
            self.check_states[index, 1] = overwrite
            self.check_states[index, 2] = not overwrite


class _Delegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(_Delegate, self).__init__(parent)

        self.editor = None

    def paint(self, painter, option, index):

        if index.column() in (0, 4):
            super(_Delegate, self).paint(painter, option, index)
            return

        data = index.model().data(index, QtCore.Qt.DisplayRole)

        checkboxstyle = QtWidgets.QStyleOptionButton()

        checkbox_rect = QtWidgets.QApplication.style().subElementRect(
            QtWidgets.QStyle.SE_CheckBoxIndicator, checkboxstyle
        )
        checkboxstyle.rect = option.rect
        checkboxstyle.rect.setLeft(option.rect.x() + option.rect.width() / 2 - checkbox_rect.width() / 2)
        #checkboxstyle.palette.setColor(QtGui.QPalette.Highlight, index.model()._data_roles(index, QtCore.Qt.BackgroundRole))

        if data:
            checkboxstyle.state = QtWidgets.QStyle.State_On | QtWidgets.QStyle.State_Enabled
        else:
            checkboxstyle.state = QtWidgets.QStyle.State_Off | QtWidgets.QStyle.State_Enabled

        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, checkboxstyle, painter)

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())


class MetaHeaderView(QtWidgets.QHeaderView):

    def __init__(self,orientation, parent=None):
        super(MetaHeaderView, self).__init__(orientation, parent)
        self.setSectionsMovable(True)
        self.setSectionsClickable(True)
        # This block sets up the edit line by making setting the parent
        # to the Headers Viewport.
        self.line = QtWidgets.QLineEdit(self.viewport())  #Create
        self.line.setAlignment(QtCore.Qt.AlignTop) # Set the Alignmnet
        self.line.setHidden(True) # Hide it till its needed
        # This is needed because I am having a werid issue that I believe has
        # to do with it losing focus after editing is done.
        self.line.blockSignals(True)
        self.sectionedit = 0
        # Connects to double click
        self.sectionDoubleClicked.connect(self.editHeader)


class DataImport(QtWidgets.QWidget):
    def __init__(self, main_data, config, *args):
        super(DataImport, self).__init__(*args)

        self.setWindowModality(QtCore.Qt.WindowModal)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.main_data = main_data
        self.config = config

        self.accepted = False

        self.table = self.ui.tableView
        """:type: QtWidgets.QTableView"""

        header = self.table.horizontalHeader()
        """:type: QtWidgets.QHeaderView"""

        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionsClickable(True)

        self.table_model = _TableModel(self.table)
        self.table.setModel(self.table_model)

        self.table.setItemDelegate(_Delegate(self.table))
        self.table.mouseReleaseEvent = self._mouse_release_event

        self.ui.pushButton_import.clicked.connect(self._import)

    def set_data(self, data, existing_ids):
        self.table_model.set_data(data, existing_ids)

    def _mouse_release_event(self, event):
        point = QtCore.QPoint(event.x(), event.y())
        index = self.table.indexAt(point)

        if index.column() < 4:
            self.table_model.toggle(index)

        QtWidgets.QTableView.mouseReleaseEvent(self.table, event)

    def _import(self):
        self.accepted = True
        self.hide()

    def get_data(self):
        return self.table_model.get_data()

    def get_options(self):
        return self.table_model.get_options()

    def set_options(self, options):
        self.table_model.set_options(options)

    def read_file(self, filename):

        try:
            f = open(filename, 'r')
            _data = f.read().split('\n')
            f.close()

            if _data[-1] in ('', '\n', '\r', '\n\r', '\r\n'):
                del _data[-1]

            if len(_data) < 2:
                return False

            if ',' in _data[1]:
                sep = ','
            elif '\t' in _data[1]:
                sep = '\t'
            elif ';' in _data[1]:
                sep = ';'
            else:
                self.config.push_error(r'Loads: loads file has unknown delimeter!  Allowable delimeters are [,;tab].')
                return False

            _data_ = []

            for data_ in _data:
                tmp = data_.split(sep)
                _data_.append(tmp)

            _data = transpose(_data_)

        except Exception:
            return False

        columns = self.main_data.columns()

        remainder = len(_data) % columns

        _data = _data[:len(_data) - remainder]

        assert len(_data) % columns == 0

        _data_ = []

        for i in range(0, len(_data), columns):
            id1 = _data[i][0]

            try:
                index = _data[i].index('')
                tmp = [_data[i][1:index]]
            except ValueError:
                tmp = [_data[i][1:]]

            for j in range(1, columns):
                assert id1 == _data[i + j][0]
                try:
                    index = _data[i + j].index('')
                    tmp.append(_data[i + j][1:index])
                except ValueError:
                    tmp.append(_data[i + j][1:])

            _data_.append([id1, tmp])

        existing_ids = {}

        for key, data in iteritems(self.main_data.data):
            existing_ids[key] = data.shape[0]

        self.set_data(_data_, existing_ids)


if __name__ == '__main__':
    import sys

    def app_exception_hook(type_, value_, tback_):
        sys.__excepthook__(type_, value_, tback_)

    sys.excepthook = app_exception_hook

    app = QtWidgets.QApplication([])

    widget = DataImport()

    data = [
        ['a', 1, 2, 3, 4, 5],
        ['b', 6, 7, 8, 9, 10],
        ['c', 11, 12, 13, 14, 15]
    ]

    existings_ids = {
        'b': 7,
        'c': 5
    }

    widget.set_data(data, existings_ids)

    widget.show()

    sys.exit(app.exec_())