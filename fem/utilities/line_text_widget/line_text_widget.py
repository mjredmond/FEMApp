"""
line_text_edit.line_text_edit

tbd

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtGui, QtWidgets, QtCore

QFrame = QtWidgets.QFrame
QWidget = QtWidgets.QWidget
QTextEdit = QtWidgets.QTextEdit
QHBoxLayout = QtWidgets.QHBoxLayout
QPainter = QtGui.QPainter


class _NumberBar(QWidget):
    def __init__(self, *args):
        super(_NumberBar, self).__init__(*args)
        self.edit = None
        # This is used to update the width of the control.
        # It is the highest line that is currently visibile.
        self.highest_line = 0

    def setTextEdit(self, edit):
        self.edit = edit

    def update(self, *args):
        '''
        Updates the number bar to display the current set of numbers.
        Also, adjusts the width of the number bar if necessary.
        '''
        # The + 4 is used to compensate for the current line being bold.
        width = self.fontMetrics().width(str(self.highest_line)) + 4
        if self.width() != width:
            self.setFixedWidth(width)
        QWidget.update(self, *args)

    def paintEvent(self, event):
        contents_y = self.edit.verticalScrollBar().value()
        page_bottom = contents_y + self.edit.viewport().height()
        font_metrics = self.fontMetrics()
        current_block = self.edit.document().findBlock(self.edit.textCursor().position())

        painter = QPainter(self)

        line_count = 0
        # Iterate over all text blocks in the document.
        block = self.edit.document().begin()
        while block.isValid():
            line_count += 1

            # The top left position of the block in the document
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()

            # Check if the position of the block is out side of the visible
            # area.
            if position.y() > page_bottom:
                break

            # We want the line number for the selected line to be bold.
            bold = False
            if block == current_block:
                bold = True
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)

            # Draw the line number right justified at the y position of the
            # line. 3 is a magic padding number. drawText(x, y, text).
            painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3,
                             round(position.y()) - contents_y + font_metrics.ascent(), str(line_count))

            # Remove the bold style if it was set previously.
            if bold:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)

            block = block.next()

        self.highest_line = line_count
        painter.end()

        QWidget.paintEvent(self, event)


class LineTextWidget(QFrame):
    def __init__(self, text_edit=None, *args):
        super(LineTextWidget, self).__init__(*args)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        if text_edit is None:
            self.edit = QTextEdit()
        else:
            self.edit = text_edit

        self.edit.setFrameStyle(QFrame.NoFrame)
        self.edit.setAcceptRichText(False)

        self.number_bar = _NumberBar()
        self.number_bar.setTextEdit(self.edit)

        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)

    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QFrame.eventFilter(object, event)

    def getTextEdit(self):
        return self.edit

    def append(self, txt):
        self.edit.setText(self.edit.toPlainText() + '\n' + txt)

    def set_text(self, txt):
        self.edit.setText(txt)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication([])
    w = LineTextWidget()
    w.show()

    sys.exit(app.exec_())
