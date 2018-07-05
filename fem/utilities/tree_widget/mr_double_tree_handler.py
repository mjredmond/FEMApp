from __future__ import print_function, absolute_import

__author__ = 'Michael Redmond'

from collections import OrderedDict

from qtpy import QtCore, QtWidgets, QtGui

from .mr_tree_view import MrTreeView

from six import iteritems

from fem.utilities import MrSignal


class MrDoubleTreeHandler(QtWidgets.QWidget):

    # data_added = QtCore.Signal(int, object)
    # data_removed = QtCore.Signal(int, object)
    # selection_changed = QtCore.Signal()

    def __init__(self, tree1, tree2, add_btn, del_btn, add_all=None, remove_all=None):
        super(MrDoubleTreeHandler, self).__init__()

        self.data_added = MrSignal()
        self.data_removed = MrSignal()
        self.selection_changed = MrSignal()

        if not isinstance(tree1, MrTreeView):
            tree1 = MrTreeView.wrap_obj(tree1)

        if not isinstance(tree2, MrTreeView):
            tree2 = MrTreeView.wrap_obj(tree2)

        self._tree1 = tree1
        self._tree2 = tree2

        self._tree1.sorting_changed.connect(self.update_trees)
        self._tree2.sorting_changed.connect(self.update_trees)

        self.pushButton_add = add_btn
        """:type: QtGui.QPushButton"""
        self.pushButton_delete = del_btn
        """:type: QtGui.QPushButton"""

        self.pushButton_add_all = add_all
        """:type: QtGui.QPushButton"""
        self.pushButton_remove_all = remove_all
        """:type: QtGui.QPushButton"""

        self.pushButton_add_clicked = MrSignal()
        self.pushButton_delete_clicked = MrSignal()
        self.pushButton_add_all_clicked = MrSignal()
        self.pushButton_remove_all_clicked = MrSignal()

        self.pushButton_add.clicked.connect(self.pushButton_add_clicked.emit)
        self.pushButton_delete.clicked.connect(self.pushButton_delete_clicked.emit)

        if self.pushButton_add_all:
            self.pushButton_add_all.clicked.connect(self.pushButton_add_all_clicked.emit)

        if self.pushButton_remove_all:
            self.pushButton_remove_all.clicked.connect(self.pushButton_remove_all_clicked.emit)

        self.pushButton_add_clicked.connect(self._add_btn_clicked)
        self.pushButton_delete_clicked.connect(self._remove_btn_clicked)
        self.pushButton_add_all_clicked.connect(self.add_all)
        self.pushButton_remove_all_clicked.connect(self.remove_all)

        self._data = OrderedDict()

    def _add_btn_clicked(self, *args):
        self.add_selection(self._tree1.get_selected_items_text())

    def _remove_btn_clicked(self, *args):
        self.remove_selection(self._tree2.get_selected_items_text())

    def get_selected_1(self):
        return self._tree1.get_selected_items_text()

    def get_selected_2(self):
        return self._tree2.get_selected_items_text()

    def add_selection(self, selected_items_text):
        data_keys = list(self._data.keys())

        if not data_keys:
            return

        selection = selected_items_text

        if not selection:
            return

        for item in selection:
            row = data_keys.index(item)
            self._data[data_keys[row]] = 1

        self.update_trees()

        first_index = data_keys.index(selection[0])
        self.data_added.emit(first_index, selection[0])

        self.selection_changed.emit()

    def remove_selection(self, selected_items_text):
        data_keys = list(self._data.keys())

        if not data_keys:
            return

        selection = selected_items_text

        if not selection:
            return

        for item in selection:
            row = data_keys.index(item)
            self._data[data_keys[row]] = 0

        self.update_trees()

        first_index = data_keys.index(selection[0])
        self.data_added.emit(first_index, selection[0])

        self.selection_changed.emit()

    def _add_all_clicked(self):
        self.add_all()

    def add_all(self, *args):
        data_keys = self._data.keys()

        for data in data_keys:
            self._data[data] = 1

        self.update_trees()

        self.selection_changed.emit()

    def _remove_all_clicked(self):
        self.remove_all()

    def remove_all(self, *args):
        data_keys = self._data.keys()

        for data in data_keys:
            self._data[data] = 0

        self.update_trees()

        self.selection_changed.emit()

    def clear(self):
        self._tree1.clear()
        self._tree2.clear()
        self._data.clear()

    def set_data(self, new_data, selected=()):
        self.clear()

        new_dict = OrderedDict()

        for data in new_data:
            new_dict[str(data)] = 0

        for data in selected:
            new_dict[str(data)] = 1

        self._data = new_dict

        self.update_trees()

    def set_data_dict(self, data_dict):

        self.clear()

        new_dict = OrderedDict()

        for key in data_dict.keys():
            new_dict[str(key)] = data_dict[key]

        self._data = new_dict

        self.update_trees()

    def get_data(self):
        return self._data.keys()

    def get_data_dict(self):
        return OrderedDict(self._data)

    def get_selected_data(self):
        data = []

        for key, item in iteritems(self._data):
            if item == 1:
                data.append(key)

        return data

    def get_selected_indices(self):
        data = []

        i = 0

        for key, item in iteritems(self._data):
            if item == 1:
                data.append(i)

            i += 1

        return data

    def get_unselected_indices(self):
        data = []

        i = 0

        for key, item in iteritems(self._data):
            if item != 1:
                data.append(i)

            i += 1

        return data

    def set_selected_indices(self, indices):

        i = 0

        _data = self._data
        for key, item in iteritems(_data):
            if i in indices:
                _data[key] = 1
            else:
                _data[key] = 0

            i += 1

        self.update_trees()

    def update_trees(self):
        tree1_data = []
        tree2_data = []

        for data in self._data.keys():
            if self._data[data]:
                tree2_data.append(data)
            else:
                tree1_data.append(data)

        self._tree1.clear()
        self._tree1.add_items(tree1_data)

        self._tree2.clear()
        self._tree2.add_items(tree2_data)

    def get_tree1(self):
        return self._tree1

    def get_tree2(self):
        return self._tree2


if __name__ == '__main__':

    app = QtWidgets.QApplication([])
    widget = QtWidgets.QWidget()

    tree1 = MrTreeView(widget)
    tree2 = MrTreeView(widget)
    add_btn = QtWidgets.QPushButton()
    add_btn.setText("Add")
    del_btn = QtWidgets.QPushButton()
    del_btn.setText("Delete")

    add_all = QtWidgets.QPushButton()
    add_all.setText("Add All")
    remove_all = QtWidgets.QPushButton()
    remove_all.setText("Remove All")

    layout = QtWidgets.QVBoxLayout(widget)
    widget.setLayout(layout)

    layout = widget.layout()
    layout.addWidget(tree1)
    layout.addWidget(tree2)
    layout.addWidget(add_btn)
    layout.addWidget(del_btn)
    layout.addWidget(add_all)
    layout.addWidget(remove_all)

    dbl_tree_handler = MrDoubleTreeHandler(tree1, tree2, add_btn, del_btn, add_all, remove_all)

    dbl_tree_handler.set_data([0, 1, 2, 3, 10, 9, 8, 7, 4, 5, 6])

    widget.show()

    import sys

    sys.exit(app.exec_())