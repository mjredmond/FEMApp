from __future__ import print_function, absolute_import

import os
from vtk import qt

if os.environ['QT_API'].lower() == 'pyqt4':
    qt.PyQtImpl = 'PyQt4'
elif os.environ['QT_API'].lower() == 'pyqt5':
    qt.PyQtImpl = 'PyQt5'
else:
    raise ValueError("Must use either PyQt4 or PyQt5!")


from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MyQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
    def __init__(self, *args, **kwargs):
        QVTKRenderWindowInteractor.__init__(self, *args, **kwargs)

    def keyPressEvent(self, ev):
        if ev.isAutoRepeat():
            return

        QVTKRenderWindowInteractor.keyPressEvent(self, ev)

    def keyReleaseEvent(self, ev):
        if ev.isAutoRepeat():
            return

        ctrl, shift = self._GetCtrlShift(ev)
        if ev.key() < 256:
            key = str(ev.text())
        else:
            key = chr(0)

        self._Iren.SetEventInformationFlipY(self._QVTKRenderWindowInteractor__saveX,
                                            self._QVTKRenderWindowInteractor__saveY,
                                            ctrl, shift, key, 0, None)
        self._Iren.KeyReleaseEvent()

    def Finalize(self):
        QVTKRenderWindowInteractor.Finalize(self)
        self._Iren.TerminateApp()
        self._Iren.SetRenderWindow(None)
        self._RenderWindow = None
        self._Iren = None
