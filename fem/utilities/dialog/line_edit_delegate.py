"""
dialog.line_edit_delegate

tbd

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtCore, QtGui, QtWidgets

import weakref

from .options_dialog import OptionsDialog

from fem.utilities import MrSignal, debuginfo


MouseButtonPress = QtCore.QEvent.MouseButtonPress
MouseButtonRelease = QtCore.QEvent.MouseButtonRelease
LeftButton = QtCore.Qt.LeftButton
RightButton = QtCore.Qt.RightButton
MiddleButton = QtCore.Qt.MiddleButton
Key_Enter = QtCore.Qt.Key_Enter
Key_Return = QtCore.Qt.Key_Return
Key_Escape = QtCore.Qt.Key_Escape


class AbstractLineEditDelegate(QtCore.QObject):
    objects = []

    def __new__(cls, *args, **kwargs):
        obj = super(AbstractLineEditDelegate, cls).__new__(cls, *args, **kwargs)
        cls.objects.append(weakref.proxy(obj))
        return obj

    @classmethod
    def finish_all_editing(cls, obj):
        count = 0
        for o in cls.objects:
            try:
                o.block_signals()
                count += o.done_editing(obj)
                o.unblock_signals()
            except ReferenceError:
                pass

        if count == 0:
            return

        try:
            cls.objects[0].get_model().value_changed.emit()
        except (IndexError, ReferenceError):
            pass

    def __init__(self, parent, data):
        """
        :param parent: QtWidgets.QLineEdit to whom the delegate belongs to
        :type parent: QtWidgets.QLineEdit
        :param data: AbstractData to whom the delegate sends _main_data to
        :type data: AbstractData
        """
        super(AbstractLineEditDelegate, self).__init__(parent)

        self._parent = parent
        self._data = data

        self._parent.setReadOnly(True)
        self._parent.mouseReleaseEvent = self._mouseReleaseEvent
        self._parent.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self._active = False
        self._enabled = True

    def execute(self, geometry=None):
        raise NotImplementedError

    def done_editing(self, obj=None):
        if not self._active or obj is self.delegate():
            return 0

        self.update_value()
        self.update_text()
        self.hide()
        return 1

    def _udpate_value(self):
        raise NotImplementedError

    def hide(self):
        raise NotImplementedError

    def text(self):
        raise NotImplementedError

    def parent_text(self):
        raise NotImplementedError

    def update_text(self):
        data_str = self._data.as_string()
        if data_str is None:
            self._parent.setText("")
            self._parent.setToolTip("")
        else:
            self._parent.setText(data_str.strip())
            self._parent.setToolTip(str(self._data.value()))

    def data(self):
        return self._data

    def delegate(self):
        raise NotImplementedError

    def block_signals(self):
        self._data.value_changed.block()

    def unblock_signals(self):
        self._data.value_changed.unblock()

    # from controller

    def clear(self):
        self._parent.setText("")

    def resize_font(self, initial_font_size=8.25):
        font_size = initial_font_size
        some_font = self._parent.font()

        while True:
            some_font.setPointSizeF(font_size)
            metric = QtGui.QFontMetrics(some_font)
            self._parent.setFont(some_font)

            if metric.width(self._parent.text()) < self._parent.width():
                break
            else:
                font_size -= 0.1

            if font_size < 5:
                break

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def _mouseReleaseEvent(self, event):
        button = event.button()

        if button == LeftButton:
            self.execute()
        elif button == RightButton:
            menu = QtWidgets.QMenu()
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")
            global_position = QtGui.QCursor().pos()
            actionCopy.triggered.connect(self._copy)
            actionPaste.triggered.connect(self._paste)
            menu.exec_(global_position)
        elif button == MiddleButton:
            pass

        event.accept()

    # copy/paste
    def _copy(self, *args):
        _value = self._data.value()
        if _value is not None:
            QtWidgets.QApplication.clipboard().setText(str(_value))

    def _paste(self, *args):
        clipboard_text = QtWidgets.QApplication.clipboard().text()
        data = str(clipboard_text.split('\n')[0].split('\t')[0])
        self._data.set_value(data)


class EmptyLineEditDelegate(AbstractLineEditDelegate):
    def __init__(self, parent, data):
        AbstractLineEditDelegate.__init__(self, parent, data)

    def execute(self, geometry=None):
        pass

    def update_value(self):
        pass

    def hide(self):
        pass

    def text(self):
        pass

    def parent_text(self):
        return self._parent.text()

    def delegate(self):
        pass

    #def update_text(self):
    #    pass


class BasicLineEditDelegate(AbstractLineEditDelegate):
    def __init__(self, parent, data):
        """
        :param parent: QtWidgets.QLineEdit to whom the delegate belongs to
        :type parent: QtWidgets.QLineEdit
        :param data: AbstractData to whom the delegate sends _main_data to
        :type data: AbstractData
        """
        AbstractLineEditDelegate.__init__(self, parent, data)

        self.setObjectName(str(parent.objectName()) + "_delegate")

        self._line_edit = QtWidgets.QLineEdit(parent.parent())
        self._line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self._line_edit.hide()
        self._line_edit.setWindowModality(QtCore.Qt.WindowModal)
        self._line_edit.keyPressEvent = self._keyPressEvent

    def execute(self, geometry=None):
        if self._enabled is False:
            return

        self._active = True

        if geometry is None:
            geometry = self._parent.geometry()

        current_value = self._data.value()
        if current_value is None:
            current_value = ""

        self._line_edit.setText(str(current_value))
        self._line_edit.setGeometry(geometry)
        self._line_edit.show()
        self._line_edit.selectAll()
        self._line_edit.setFocus()

    def delegate(self):
        return self._line_edit

    def update_value(self):
        # each _main_data value must be able to convert from str to its proper _main_data type
        self._data.set_value(self.text())

    def hide(self):
        self._active = False
        self._line_edit.hide()

    def text(self):
        return str(self._line_edit.text())

    def parent_text(self):
        return self._parent.text()

    def _keyPressEvent(self, event):
        key = event.key()

        if key == Key_Enter or key == Key_Return:
            self.hide()
            self.update_value()
            event.accept()
            return

        if key == Key_Escape:
            self.hide()
            event.accept()
            return

        QtWidgets.QLineEdit.keyPressEvent(self._line_edit, event)


class OptionsLineEditDelegate(AbstractLineEditDelegate):
    def __init__(self, parent, data, options_data, dialog_title):
        """
        :param parent: QtWidgets.QLineEdit to whom the delegate belongs to
        :type parent: QtWidgets.QLineEdit
        :param data: AbstractData to whom the delegate sends _main_data to
        :type data: AbstractData
        """
        AbstractLineEditDelegate.__init__(self, parent, data)

        self.setObjectName(str(parent.objectName()) + "_delegate")

        self._dialog_title = dialog_title
        self._dialog = None
        self._options_data = options_data

        self.update_value = MrSignal()

        self._return_list = False

        if hasattr(self._options_data, 'return_data_list'):
            if self._options_data.return_data_list is True:
                self._return_list = True

    def execute(self, geometry=None):
        if self._enabled is False:
            return

        self._active = True

        self._dialog = OptionsDialog(self._dialog_title, parent=self._parent)
        self._dialog.skip_click = True
        self._dialog.finished.connect(self._update_value)

        options_data = self._options_data()

        data = options_data['_main_data']()
        headers = options_data['headers']
        widths = options_data['widths']
        initial_values = options_data['initial_values']()

        self._dialog.set_data(data)
        self._dialog.set_up_data_lists(headers, widths)
        self._dialog.initial_values(initial_values)
        self._dialog.align_to(self._parent)
        self._dialog.setFocus()
        self._dialog.exec_()

    def delegate(self):
        return self._dialog

    def done_editing(self, obj=None):
        return 0

    def _update_value(self, *args):
        try:
            if not self._return_list:
                value = self._dialog.return_data
                if value is None:
                    return
                self.update_value.emit(str(value))
            else:
                self.update_value.emit(map(str, self._dialog.return_data_list))
        except AttributeError:
            pass

    def hide(self):
        self._active = False
        try:
            self._dialog.hide()
        except AttributeError:
            pass

    def text(self):
        try:
            if not self._return_list:
                value = self._dialog.return_data
                if value is None:
                    return ""
                return str(value)
            else:
                list_ = self._dialog.return_data_list
                return "/".join(map(str, list_))
        except AttributeError:
            return ""

    def parent_text(self):
        return self._parent.text()


class HeaderLineEditDelegate(BasicLineEditDelegate):
    def __init__(self, parent, data, table):
        BasicLineEditDelegate.__init__(self, parent, data)

        self._table = table
        self.current_value = ""

    def execute(self, geometry=None):
        BasicLineEditDelegate.execute(self, geometry)
        self._line_edit.setText(self.current_value)

    def value(self):
        return self._data.value()

    def update_value(self, *args):
        pass

    def as_string(self):
        return self._data.as_string()

    def done_editing(self, obj=None):
        if obj is self._delegate.widget():
            return

        self._delegate.update_value()
        self._delegate.done_editing.emit()

    def delegate(self):
        return self._delegate.widget()

    def set_value(self, value):
        self._undo_redo.set_value(value)

    def _done_editing(self):
        if not self._active:
            return

        if self._data is None:
            return

        self._delegate.update_value()

        try:
            new_value = self._delegate.value()
            if isinstance(new_value, list):
                new_value = self._data.convert(new_value[-1])
            else:
                new_value = self._data.convert(new_value)
        except (ValueError, TypeError):
            self._delegate.hide()
            return

        self.set_value(new_value)

        self._delegate.hide()
        self._active = False
