from __future__ import print_function, absolute_import

from qtpy import QtCore, QtWidgets, QtGui

from fem.utilities.line_text_widget import LineTextWidget

from fem.base_app.configuration import BaseConfiguration, timestamp
from fem.utilities import BaseObject, MrSignal


class BaseLoggingDock(QtWidgets.QDockWidget, BaseObject):
    BaseConfiguration = BaseConfiguration

    def __init__(self, main_window):
        super(BaseLoggingDock, self).__init__(main_window)

        self.main_window = main_window

        self.log = LineTextWidget(None, self)
        self.setWidget(self.log)

        self.setWindowTitle('Log')

        self.log.edit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.log.edit.setReadOnly(True)

        self.config = self.BaseConfiguration.instance()
        """:type: app_template.configuration.Configuration"""

        self.config.dispatcher.action_added.connect(self._action_added)
        self.config.msg.connect(self._message)

        self.action_done = MrSignal()

    def log_text(self):
        return str(self.log.edit.toPlainText())

    def _action_added(self, action_str):

        # action_name = action[0]
        # try:
        #    action_data = action[1]
        # except IndexError:
        #     action_data = '()'

        new_txt = "%s:  %s" % (timestamp(), action_str)

        self._print_msg(new_txt)

        self.config.flush_msgs()

        self.action_done.emit(action_str)

    def _print_msg(self, msg):
        edit = self.log.edit

        old_txt = str(edit.toPlainText())

        if old_txt == '':
            old_txt = msg
        else:
            old_txt += '\n' + msg

        edit.setText(old_txt)

        scroll_bar = edit.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def _message(self, msg):
        if msg.startswith('Info') or msg.startswith('Error'):
            self._print_msg('%-22s%s' % ('', msg))
            return

        msg = "%s:  %s" % (timestamp(), msg)
        self._print_msg(msg)

    @classmethod
    def copy_cls(cls):
        class _Tmp(cls):
            pass

        _Tmp.__name__ = cls.__name__

        return _Tmp
