"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtCore, QtGui


class FreezeTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(FreezeTableView, self).__init__(parent)

        self._frozen = QtWidgets.QTableView(self)

        self._frozen.setFocusPolicy(QtCore.Qt.NoFocus)
        self._frozen.verticalHeader().hide()
        self._frozen.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        self.viewport().stackUnder(self._frozen)

        self._frozen.setStyleSheet(
            """
            QTableView { border: none;
                         background-color: #8EDE21;
                         selection-background-color: #999
                        }
            """
        )

        self._frozen.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._frozen.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._frozen.show()

        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self._frozen.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        self.horizontalHeader().sectionResized.connect(self._update_frozen_geometry)
        self.verticalHeader().sectionResized.connect(self._update_frozen_geometry)

        self.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.verticalScrollBar().valueChanged.connect(self._frozen.verticalScrollBar().setValue)

    def setModel(self, model):
        super(FreezeTableView, self).setModel(model)
        self._frozen.setModel(model)
        self._frozen.setSelectionModel(self.selectionModel())

        for i in range(1, model.columnCount()):
            self._frozen.setColumnHidden(i, True)

        self._frozen.setColumnWidth(0, self.columnWidth(0))

        self._update_frozen_geometry()

    def updateSectionWidth(self, logicalIndex, oldSize, newSize):
        if logicalIndex == 0:
            self._frozen.setColumnWidth(0, newSize)
            self._update_frozen_geometry()

    def updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self._frozen.setRowHeight(logicalIndex, newSize)

    def resizeEvent(self, event):
        super(FreezeTableView, self).resizeEvent(event)
        self._update_frozen_geometry()

    def moveCursor(self, cursorAction, modifiers):
        current = super(FreezeTableView, self).moveCursor(cursorAction, modifiers)

        if cursorAction == QtWidgets.QAbstractItemView.MoveLeft and current.column() > 0 \
                and self.visualRect(current).topLeft().x() < self._frozen.columnWidth(0):
            newValue = self.horizontalScrollBar().value() + self.visualRect(current).topLeft().x() \
                       - self._frozen.columnWidth(0)
            self.horizontalScrollBar().setValue(newValue)

        return current

    def scrollTo(self, index, hint):
        if index.column() > 0:
            super(FreezeTableView, self).scrollTo(index, hint)

    def _update_frozen_geometry(self):
        self._frozen.setGeometry(
            self.verticalHeader().width() + self.frameWidth(),
            self.frameWidth(),
            self.columnWidth(0),
            self.viewport().height() + self.horizontalHeader().height()
        )


class _Model(QtCore.QAbstractTableModel):
    def __init__(self, *args):
        super(_Model, self).__init__(*args)

        import numpy as np

        self._data = np.zeros((10, 10), dtype=np.float64)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self._data.shape[0]

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self._data.shape[1]

    def flags(self, QModelIndex):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def headerData(self, p_int, Qt_Orientation, int_role=None):
        if int_role == QtCore.Qt.DisplayRole:
            return p_int + 1

        return None

    def data(self, QModelIndex, int_role=None):
        if int_role in (QtCore.Qt.EditRole, QtCore.Qt.DisplayRole):
            row, col = QModelIndex.row(), QModelIndex.column()
            return str(self._data[row, col])

        return None

    def setData(self, QModelIndex, QVariant, int_role=None):
        if int_role == QtCore.Qt.EditRole:
            row, col = QModelIndex.row(), QModelIndex.column()
            self._data[row, col] = QVariant
            return True

        return False


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication([])

    table = FreezeTableView()
    model = _Model(table)
    table.setModel(model)
    table.show()

    sys.exit(app.exec_())
