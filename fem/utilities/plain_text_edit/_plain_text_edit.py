from __future__ import print_function, absolute_import

from qtpy import QtCore, QtGui, QtWidgets


class PlainTextEdit(QtWidgets.QPlainTextEdit):
    """
    A PlainTextEdit editor that sends editingFinished events
    when the text was changed and focus is lost.
    """

    editingFinished = QtCore.Signal()
    receivedFocus = QtCore.Signal()
    returnPressed = QtCore.Signal()

    @classmethod
    def wrap_obj(cls, obj=None, *args, **kwargs):
        """

        :rtype: PlainTextEdit
        """

        if obj is None:
            obj = PlainTextEdit(*args, **kwargs)
            return obj

        elif isinstance(obj, PlainTextEdit):
            return obj

        assert isinstance(obj, QtWidgets.QPlainTextEdit)

        parent = obj.parent()

        obj.__class__ = PlainTextEdit
        PlainTextEdit.init(obj)

        return obj

    def __init__(self, parent):
        super(PlainTextEdit, self).__init__(parent)
        self._changed = False
        self.init()

    def init(self):
        self._changed = False
        self.setTabChangesFocus(True)
        self.textChanged.connect(self._handle_text_changed)

    def focusInEvent(self, event):
        super(PlainTextEdit, self).focusInEvent(event)
        self.receivedFocus.emit()

    def focusOutEvent(self, event):
        if self._changed:
            self.editingFinished.emit()
        super(PlainTextEdit, self).focusOutEvent(event)

    def _handle_text_changed(self):
        self._changed = True

    def setTextChanged(self, state=True):
        self._changed = state

    def setHtml(self, html):
        QtWidgets.QPlainTextEdit.setHtml(self, html)
        self._changed = False

    def keyPressEvent(self, QKeyEvent):
        """

        :param QKeyEvent:
        :type QKeyEvent: QtGui.QKeyEvent
        :return:
        :rtype:
        """

        if QKeyEvent.key() == QtCore.Qt.Key_Enter:
            self.returnPressed.emit()
        else:
            super(PlainTextEdit, self).keyPressEvent(QKeyEvent)
