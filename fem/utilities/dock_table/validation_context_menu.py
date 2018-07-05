"""
dock_table.validation_context_menu

Validation context menu

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from qtpy import QtWidgets, QtGui


class Undefined(object):
    pass


undefined = Undefined()


def validation_context_menu(validation_data):

    if len(validation_data) == 0:
        return False, None

    selected_value = [undefined, undefined]

    menu = QtWidgets.QMenu()
    font = QtGui.QFont("Monospace")
    font.setStyleHint(QtGui.QFont.TypeWriter)
    menu.setFont(font)

    for i in range(len(validation_data)):
        data = validation_data[i]

        def make_selection(data, i):
            data_ = str(data)
            i_ = i

            def make_selection_():
                selected_value[0] = data_
                selected_value[1] = i_

            return make_selection_

        menu.addAction("%s" % str(data), make_selection(data, i))

    position = QtGui.QCursor.pos()
    menu.exec_(position)

    if selected_value[0] is undefined:
        return False, [None, None]
    else:
        return True, selected_value
