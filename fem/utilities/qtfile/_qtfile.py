"""
Project.x

Author: Michael Redmond

"""

from qtpy import QtCore, QtGui, QtWidgets


def getsavefilename(caption='', directory='', filter_=''):
    result = QtWidgets.QFileDialog.getSaveFileName(
        caption=caption,
        directory=directory,
        filter=filter_
    )

    if isinstance(result, tuple):
        return str(result[0])
    else:
        return str(result)


def getopenfilename(caption='', directory='', filter_=''):
    result = QtWidgets.QFileDialog.getOpenFileName(
        caption=caption,
        directory=directory,
        filter=filter_
    )

    if isinstance(result, tuple):
        return str(result[0])
    else:
        return str(result)
