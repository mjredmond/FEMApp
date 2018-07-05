from __future__ import print_function, absolute_import

import json
import os
from qtpy import QtCore, QtWidgets

from fem.configuration import config
from .logging_dock import timestamp


class HelpMenu(object):
    def __init__(self, main_window):
        self.main_window = main_window

        self.menu_bar = self.main_window.menuBar()
        """:type: QtWidgets.QMenuBar"""

        self.help_menu = self.menu_bar.addMenu("&Help")

        self.actionUserManual = self.help_menu.addAction('User Manual')
        self.actionUserManual.triggered.connect(self._user_manual)

        self.actionFeedback = self.help_menu.addAction('Issues/Feedback')
        self.actionFeedback.triggered.connect(self._feedback)

        self.actionAbout = self.help_menu.addAction('About')
        self.actionAbout.triggered.connect(self._about)

        self.config = config
        self.dispatch = self.config.dispatcher.dispatch

    def _user_manual(self):
        _open_link(self.config.user_manual())

    def _feedback(self):
        dialog = FeedbackDialog(self.main_window)
        dialog.show()
        dialog.raise_()

        while True:
            if not dialog.isVisible():
                break
            self.config.app().processEvents()

    def _about(self):
        QtWidgets.QMessageBox.about(self.main_window, self.config.application_name(), self.config.about())


def _open_link(url):
    try:
        os.system("start " + url)
    except:
        pass


class FeedbackDialog(QtWidgets.QWidget):
    def __init__(self, main_window, *args):
        super(FeedbackDialog, self).__init__(*args)

        self.main_window = main_window

        layout = QtWidgets.QGridLayout(self)
        le = QtWidgets.QLabel(self)
        le.setText('Provide feedback or a description of the error.')
        layout.addWidget(le)

        self.text_edit = QtWidgets.QTextEdit(self)
        layout.addWidget(self.text_edit)

        self.setWindowTitle('Issues/Feedback')

        hlayout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton(self)
        ok_btn.setText('Ok')
        hlayout.addWidget(ok_btn)
        cancel_btn = QtWidgets.QPushButton(self)
        cancel_btn.setText('Cancel')
        hlayout.addWidget(cancel_btn)

        layout.addItem(hlayout)

        ok_btn.clicked.connect(self._ok)
        cancel_btn.clicked.connect(self._cancel)

        self.accepted = False

        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def _ok(self):
        self.accepted = True
        self.close()

    def _cancel(self):
        self.accepted = False
        self.close()

    def closeEvent(self, event):

        if self.accepted:
            ts = timestamp().replace(' ', '_').replace(':', '.')

            config = self.config

            folder = config.issues_and_feedback()

            filename = config.program_name().replace(' ', '_').lower()
            filename = '%s_%s.json' % (filename, ts)

            filename = os.path.join(folder, filename)

            data = {
                'application_info': config.application_info(),
                'message': str(self.text_edit.toPlainText()),
                'log': str(self.main_window.log_text())
            }

            with open(filename, 'w') as f:
                f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

        try:
            super(FeedbackDialog, self).closeEvent(event)
        except TypeError:
            pass
