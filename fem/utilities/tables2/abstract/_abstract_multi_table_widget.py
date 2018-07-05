from qtpy import QtWidgets, QtCore, QtGui

from ._abstract_table_widget import AbstractTableWidget


class AbstractMultiTableWidget(QtWidgets.QWidget):
    
    TableWidget = AbstractTableWidget
    SecondaryMultiTableWidget = None

    def __init__(self, main_window, *args):
        super().__init__(*args)

        self.main_window = main_window

        self.table_1 = self.TableWidget(self)
        self.table_2 = None
        """:type: AbstractMultiTableWidget"""

        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._splitter.addWidget(self.table_1)
        # self._splitter.addWidget(self.table_2)

        self.setLayout(QtWidgets.QHBoxLayout())

        self.layout().addWidget(self._splitter)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # self.table_2.hide()

        #####

        self.table_1.table.selection_changed.connect(self._selection_1_changed)

    def _add_table_2(self):
        if self.table_2 is not None:
            return

        # FIXME: main_window needs to be here
        
        if self.SecondaryMultiTableWidget is None:
            self.SecondaryMultiTableWidget = self.__class__

        self.table_2 = self.SecondaryMultiTableWidget(self.main_window, self)
        self._splitter.addWidget(self.table_2)
        self.table_2.hide()

    def _hide_table_2(self):
        if self.table_2 is None:
            return

        self.table_2.hide()

    def update_all(self):
        self.table_1.update_all()
        try:
            self.table_2.update_all()
        except AttributeError:
            pass

    def _selection_1_changed(self, index):
        subdata = self._subdata(index)
        
        if subdata is None:
            self._hide_table_2()
            return

        self._add_table_2()
        
        self.table_2.set_model_data(subdata, False)
        self.table_2.update_all()
        self.table_2.show()

    ####################################

    def _subdata(self, index=None):
        if index is None:
            index = self._index1()
        return self.table_1.table.model().subdata(index)

    def _index1(self):
        return self.table_1.table.current_index()

    def _index2(self):
        try:
            return self.table_2.table_1.table.current_index()
        except AttributeError:
            return None
    
    def set_model_data(self, data, update_all=True):
        self.table_1.set_model_data(data, update_all)
        self._selection_1_changed(self._index1())
