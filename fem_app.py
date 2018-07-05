from __future__ import print_function, absolute_import


if __name__ == '__main__':
    import sys

    # h5Nastran needs to be in the path, and pyNastran for that matter
    sys.path.append(r'P:\redmond\pyNastran\h5Nastran')

    from fem import get_app

    app, mw = get_app()

    if None not in (app, mw):
        mw.show()
        sys.exit(app.exec_())
