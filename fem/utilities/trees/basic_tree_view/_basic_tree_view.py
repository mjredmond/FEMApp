"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range

from qtpy import QtGui, QtCore, QtWidgets


MouseButtonRelease = QtCore.QEvent.MouseButtonRelease
MouseButtonPress = QtCore.QEvent.MouseButtonPress
RightButton = QtCore.Qt.RightButton


def list_to_list_of_tuples(some_list):
    return [(str(something), None) for something in some_list]


class BasicSelectionModel(QtCore.QItemSelectionModel):
    def __init__(self, tree_view, model):
        super(BasicSelectionModel, self).__init__(model)

        self.tree_view = tree_view
        """:type: BasicTreeView"""

    def select(self, selection, selection_flags):
        if self.tree_view.right_button:
            return

        super(BasicSelectionModel, self).select(selection, selection_flags)


class BasicTreeModel(QtGui.QStandardItemModel):
    def __init__(self):
        super(BasicTreeModel, self).__init__()


class BasicTreeView(QtWidgets.QTreeView):

    item_changed = QtCore.Signal(str, str)
    selection_changed = QtCore.Signal(object, object)
    sorting_changed = QtCore.Signal(object)

    @classmethod
    def wrap_obj(cls, obj=None, *args, **kwargs):
        """

        :rtype: BasicTreeView
        """

        if obj is None:
            obj = BasicTreeView(*args, **kwargs)
            return obj

        elif isinstance(obj, BasicTreeView):
            return obj

        try:
            assert isinstance(obj, QtWidgets.QTreeView)
        except AssertionError:
            print(obj.__class__)
            raise

        parent = obj.parent()

        obj.__class__ = BasicTreeView
        BasicTreeView.__init__(obj, parent, False)

        return obj

    def __init__(self, parent=None, init=True):
        if init:
            super(BasicTreeView, self).__init__(parent)

        self.setSelectionMode(QtWidgets.QTreeView.SingleSelection)

        self._model = BasicTreeModel()
        self.setModel(self._model)

        self._multi_select = True

        self.model().itemChanged.connect(self._item_changed)

        self._sorted = False

        header = self.header()

        header.setSectionsClickable(True)

        header.sectionClicked.connect(self.toggle_sorting)

        self._old_text = ''

        self.add_checks = False

        self.right_button = False

        self.selection_model = BasicSelectionModel(self, self.model())
        self.setSelectionModel(self.selection_model)
        self.selectionModel().selectionChanged.connect(self._selection_changed)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

        self.data_type = str

        self._selected = set()

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copy()
            return
        elif event.matches(QtGui.QKeySequence.Paste):
            self.paste()
            return

        super(BasicTreeView, self).keyPressEvent(event)

    def copy(self):
        selected_items = self.get_selected_items_text()

        copied_text = ''
        for item in selected_items:
            copied_text += item + '\n'

        copied_text = copied_text[:-1]

        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(copied_text, mode=cb.Clipboard)

    def paste(self):
        import re
        cb = QtWidgets.QApplication.clipboard()
        clipboard_data = re.split('[,\t\n]', str(cb.text(mode=cb.Clipboard)))

        all_data = self.get_items_text()

        model = self.model()
        """:type: MrTreeModel"""

        model_selection = self.selectionModel()
        """:type: QtGui.QItemSelectionModel"""

        selection_flag = QtCore.QItemSelectionModel.Select

        self.blockSignals(True)

        for data in clipboard_data:
            try:
                index = all_data.index(data)
            except ValueError:
                continue

            index = model.index(index, 0)

            model_selection.select(index, selection_flag)

        self.blockSignals(False)

    def _context_menu(self, pos):
        menu = QtWidgets.QMenu()
        copy_action = menu.addAction('Copy')
        paste_action = menu.addAction('Paste')

        copy_action.triggered.connect(self.copy)
        paste_action.triggered.connect(self.paste)

        global_pos = self.mapToGlobal(pos)
        global_pos.setY(global_pos.y() + 25)

        menu.exec_(global_pos)

    def _selection_changed(self, selected, deselected):
        selected = [index.row() for index in selected.indexes()]
        deselected = [index.row() for index in deselected.indexes()]
        self.selection_changed.emit(selected, deselected)

        try:
            first = selected[0]
            self._old_text = self.get_items_text()[first]
        except IndexError:
            self._old_text = ''

    def _item_changed(self, item):
        if isinstance(item, QtGui.QStandardItem):
            item_text = item.text()
        else:
            item_text = str(item)

        items = self.get_items_text()

        if items.count(item_text) > 1:
            self.blockSignals(True)
            item.setText(self._old_text)
            self.blockSignals(False)
            self.refresh()
            return

        self.item_changed.emit(self._old_text, item_text)

    def select_row(self, row_index):
        selection = self.selection_model
        model = self.model()
        index1 = model.index(row_index, 0)
        index2 = model.index(row_index, model.columnCount()-1)
        selection.select(QtCore.QItemSelection(index1, index2), QtCore.QItemSelectionModel.Select)
        #selection.select(index1, index2)

    def toggle_sorting(self):
        self._sorted = not self._sorted
        self.sorting_changed.emit(self)

    def _sort_items(self, items):
        if self._sorted:
            try:
                items = map(int, items)
            except Exception:
                try:
                    items = map(float, items)
                except Exception:
                    pass

            return sorted(items)
        else:
            return items

    def add_items(self, items, parent=None, checks=None):

        if isinstance(items, list):
            items = list_to_list_of_tuples(self._sort_items(items))

        if parent is None:
            parent = self.model()

        appendRow = parent.appendRow
        QStandardItem = QtGui.QStandardItem
        add_items = self.add_items

        count = len(items)

        add_checks = self.add_checks

        for i in range(count):
            text, children = items[i]
            item = QStandardItem(text)
            self._old_text = text
            if add_checks:
                if checks:
                    check_state = checks[i]
                else:
                    check_state = True
                item.setCheckable(True)
                item.setCheckState(check_state)
            appendRow(item)
            if children:
                add_items(children, item)

    def refresh(self):
        items = self.get_items_text()

        if self.add_checks:
            check_states = self.get_check_states()
        else:
            check_states = None

        self.clear()
        self.add_items(items, checks=check_states)

    def clear(self):
        self.model().removeRows(0, self.model().rowCount())

    def mousePressEvent(self, event):

        if self._multi_select:
            if event.modifiers() & QtCore.Qt.CTRL:
                self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
            elif event.modifiers() & QtCore.Qt.SHIFT:
                self.setSelectionMode(QtWidgets.QTreeView.ContiguousSelection)
            else:
                self.setSelectionMode(QtWidgets.QTreeView.SingleSelection)

        if event.button() == RightButton:
            self.right_button = True

        super(BasicTreeView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.right_button = False

        super(BasicTreeView, self).mouseReleaseEvent(event)

    def get_selected_rows(self):
        return sorted([item.row() for item in self.selectionModel().selectedRows()])

    def get_selected_items_text(self):
        rows = self.get_selected_rows()
        items = self.get_items_text()

        return [items[row] for row in rows]

    def get_items_text(self):

        data_type = self.data_type

        items_text = []

        row_count = self.model().rowCount()

        for i in range(row_count):
            idx = self.model().index(i, 0)

            if idx.isValid():
                items_text.append(data_type(str(idx.data(QtCore.Qt.DisplayRole))))

        return items_text

    def get_check_states(self):
        check_states = []

        row_count = self.model().rowCount()

        model = self.model()
        """:type: MrTreeModel"""

        for i in range(row_count):

            item = model.item(i, 0)

            check_states.append(item.checkState())

        return check_states

    def multi_select_on(self):
        self._multi_select = True

    def multi_select_off(self):
        self._multi_select = False

    def set_header(self, header_txt):
        self.model().setHorizontalHeaderItem(0, QtGui.QStandardItem(header_txt))


if __name__ == '__main__':
    def item_changed(item):
        print(item.text())

    def selection_changed(selected, deselected):
        print(selected)
        print(deselected)

    import sys

    app = QtWidgets.QApplication([])

    tree_view = BasicTreeView.wrap_obj(QtWidgets.QTreeView())
    tree_view.item_changed.connect(item_changed)
    tree_view.selection_changed.connect(selection_changed)

    data = [['1', '2', '3', '4', '5'], '2', '3', '4', '5']

    tree_view.add_items(data)

    tree_view.show()

    sys.exit(app.exec_())