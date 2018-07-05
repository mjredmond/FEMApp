from __future__ import print_function, absolute_import

import sys

if sys.version_info[0] == 2:
    import os
    os.environ['QT_API'] = 'pyqt4'
    appstyle = 'cleanlooks'
else:
    appstyle = 'fusion'

# from qtpy import QtWidgets
# print(QtWidgets.QStyleFactory.keys())


def get_app():
    import sys
    import os.path

    from .configuration import config

    release_file = config.release_file()

    if release_file is None:
        release_file = ''

    if sys.executable != release_file and os.path.isfile(release_file):
        import subprocess

        p = subprocess.Popen([release_file], cwd=os.path.dirname(release_file))
        p.wait()

        return None, None

    else:

        # for some reason PyQt5 prevents tracebacks from showing unless an exception hook is set
        def app_exception_hook(type_, value_, tback_):
            sys.__excepthook__(type_, value_, tback_)

        sys.excepthook = app_exception_hook

        from fem.gui import MainWindow

        app = config.app()
        app.setStyle(appstyle)

        mw = MainWindow()

        config.set_icon()

        return app, mw


if __name__ == '__main__':
    import sys

    app, mw = get_app()

    if None not in (app, mw):
        mw.show()
        sys.exit(app.exec_())
