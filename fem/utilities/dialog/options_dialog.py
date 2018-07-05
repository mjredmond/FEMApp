"""
dialog.options_dialog

tbd

author: Michael Redmond

"""

from __future__ import print_function, absolute_import


from qtpy import QtCore, QtWidgets, QtGui
import collections

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class OptionsDialog(QtWidgets.QDialog):

    finished = QtCore.Signal()
    canceled = QtCore.Signal()

    width = 200
    x0 = 10
    y0 = 10

    def __init__(self, name='', data=None, parent=None):
        super(OptionsDialog, self).__init__(parent)

        self._data_lists = []
        self._headers = []
        self._widths = []
        self._data = data
        self._list_number = 0
        self.return_data = None
        self.return_data_list = None

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(name)

    def initial_values(self, initial_values):
        if initial_values is None or self._data_lists is None:
            return

        for i in range(0, len(initial_values)):
            if initial_values[i] is not None:
                try:
                    list = self._data_lists[i]['list']
                except IndexError:
                    return

                assert(isinstance(list, QtWidgets.QListWidget))
                if i == 0:
                    try:
                        list.setCurrentItem(list.item(self._data[i].index(initial_values[i])))
                    except ValueError:
                        pass
                else:
                    last_list = self._data_lists[i-1]['list']
                    assert(isinstance(last_list, QtWidgets.QListWidget))
                    last_item = str(last_list.currentItem().text())
                    try:
                        list.setCurrentItem(list.item(self._data[i][last_item].index(initial_values[i])))
                    except ValueError:
                        pass

    def set_data(self, data):
        self._data = data

    def set_up_data_lists(self, headers=None, widths=None):
        for i in range(0, len(self._data_lists)):
            self._data_lists[0]['list'].deleteLater()
            self._data_lists[0]['header'].deleteLater()
            del self._data_lists[0]['list']
            del self._data_lists[0]['header']
            del self._data_lists[0]

        if headers is None:
            self._headers = []
        else:
            self._headers = headers

        if widths is None:
            self._widths = []
        else:
            self._widths = widths

        x = 0

        for i in range(0, len(self._headers)):
            try:
                width = self._widths[i]
            except Exception:
                width = self.width

            try:
                header_text = self._headers[i]
            except Exception:
                header_text = str(i)

            header = QtWidgets.QLabel(self)
            header.setGeometry(QtCore.QRect(self.x0 + x, self.y0, width, 20))
            header.setText(header_text)
            header.setAlignment(QtCore.Qt.AlignCenter)

            data_list = QtWidgets.QListWidget(self)
            data_list.setGeometry(QtCore.QRect(self.x0 + x, self.y0 + 21, width, 200))

            #QtCore.QObject.connect(data_list, QtCore.SIGNAL(_fromUtf8("itemSelectionChanged()")),
            #                       lambda y=i: self.update_list_number(y))

            data_list.itemSelectionChanged.connect(lambda y=i: self.update_list_number(y))

            data = {'header': header, 'list': data_list}

            self._data_lists.append(data)

            x += width + 10

        try:
            self._data_lists[0]['list'].addItems(self._data[0])
        except IndexError:
            pass

        self.buttonBox.setGeometry(QtCore.QRect(x - 100, self.y0 + 230, 100, 50))

        self.setGeometry(QtCore.QRect(10, 10, x + 50, 300))

    def update_list_number(self, item):
        self._list_number = item
        self.update_list()

    def update_list(self):
        list_number = self._list_number

        for i in range(list_number+1, len(self._data_lists)):

            try:
                last_value = str(self._data_lists[i-1]['list'].currentItem().text())
                data_list = self._data[i][last_value]
            except Exception:
                last_value = ''
                data_list = self._data[i]

            if type(data_list) is dict or type(data_list) is collections.OrderedDict:
                data_list = []

            try:
                current_value = str(self._data_lists[i]['list'].currentItem().text())
            except Exception:
                current_value = ''

            self._data_lists[i]['list'].clear()
            self._data_lists[i]['list'].addItems(data_list)

            if current_value in data_list:
                self._data_lists[i]['list'].setCurrentRow(data_list.index(current_value))
            else:
                self._data_lists[i]['list'].setCurrentRow(-1)

    def align_to(self, widget):
        point = widget.rect().bottomRight()
        global_point = widget.mapToGlobal(point)
        self.move(global_point - QtCore.QPoint(self.rect().width()/2 + widget.rect().width()/2, 0))

    def accept(self):
        list_number = len(self._data_lists)-1
        try:
            self.return_data = str(self._data_lists[list_number]['list'].currentItem().text())
            self.return_data_list = [str(self._data_lists[0]['list'].currentItem().text())]
            for i in range(1, len(self._data_lists)):
                self.return_data_list.append(str(self._data_lists[i]['list'].currentItem().text()))
            self.hide()
        except Exception:
            self.return_data = None

        self.finished.emit()

    def reject(self):
        self.return_data = None
        self.hide()

        self.canceled.emit()

    def hide(self):
        super(OptionsDialog, self).hide()

    def return_value(self):
        if not self.return_data_list:
            value = self.return_data
            if value is None:
                return [None]
            return str(value)
        else:
            return self.return_data_list


def show_dialog(dialog_title=None, options_data=None, parent=None):

    assert None not in (dialog_title, options_data, parent)

    dialog = OptionsDialog(dialog_title, parent=parent)
    dialog.skip_click = True

    options_data_ = options_data()

    data = options_data_['_data_roles']()
    headers = options_data_['headers']
    widths = options_data_['widths']
    initial_values = options_data_['initial_values']()

    dialog.set_data(data)
    dialog.set_up_data_lists(headers, widths)
    dialog.initial_values(initial_values)
    dialog.align_to(parent)
    dialog.setFocus()
    dialog.exec_()

    return dialog.return_value()


if __name__ == "__main__":
    import sys

    headers = ['header 1', 'header 2', 'header 3']
    widths = [20, 30, 20, 30]
    data1 = ['11', '12', '13', '14']
    data2 = {}
    data2['11'] = ['11 1', '11 2', '11 3']
    data2['12'] = ['12 1', '12 2']
    data2['13'] = ['13 1', '13 2', '13 3', '13 4']
    data2['14'] = ['14 1']
    data3 = {}
    data3['11 1'] = ['11 1 1', '11 1 2']
    data3['11 2'] = ['11 2 1', '11 2 2', '11 2 3']
    data3['11 3'] = ['11 3 1', '11 3 2', '11 3 3']
    data3['12 1'] = ['12 1 1']
    data3['12 2'] = ['12 2 1']
    data3['13 1'] = ['13 1 1']
    data3['13 2'] = ['13 2 1']
    data3['13 3'] = ['13 3 1']
    data3['13 4'] = ['13 4 1']
    data3['14 1'] = ['14 1 1']

    data = [data1, data2, data3]

    headers = ['header 1', 'header 2']
    widths = [50, 50, 50]
    data1 = ['11', '12', '13', '14']
    data2 = {}
    data2['11'] = ['11 1', '11 2', '11 3']
    data2['12'] = ['12 1', '12 2']
    data2['13'] = ['13 1', '13 2', '13 3', '13 4']
    data2['14'] = ['14 1']

    data = [data1, data2]

    app = QtWidgets.QApplication(sys.argv)
    dialog = OptionsDialog("test", data)

    dialog.set_up_data_lists(headers, widths)

    dialog.exec_()

    print(dialog.return_data_list)

    sys.exit(app.exec_())

