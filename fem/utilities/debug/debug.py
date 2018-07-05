"""
debug.debug

Debugging utilities

author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from inspect import getframeinfo, stack
import traceback
import sys

try:
    import builtins
except ImportError:
    import __builtins__
    builtins = __builtins__


try:
    _print = builtins._print
except AttributeError:
    _print = builtins.print


def debuginfo(*msg):

    """
    prints message with filename and lineno where called from
    """

    if len(msg) == 1:
        message = str(msg[0])
    else:
        message = str(msg)[1:-1]

    caller = getframeinfo(stack()[1][0])
    _print("%s:%d - %s" % (caller.filename, caller.lineno, message))


def show_caller(func):

    """
    function decorator to show caller of function, plus filename and lineno for decorator
    """

    caller = getframeinfo(stack()[1][0])
    filename = caller.filename
    lineno = caller.lineno

    def wrapped_func(*args, **kwargs):
        _print("%s:%d - show_caller decorator" % (filename, lineno))
        caller = getframeinfo(stack()[1][0])
        _print("%s:%d - %s\n\n" % (caller.filename, caller.lineno, func.__name__))
        return func(*args, **kwargs)

    return wrapped_func


def show_stack_trace(func):

    """
    function decorator to show full stack trace, plus filename and lineno for decorator
    """

    caller = getframeinfo(stack()[1][0])
    filename = caller.filename
    lineno = caller.lineno

    def wrapped_func(*args, **kwargs):
        sys.stdout.flush()
        _print('################################################################################')
        _print('################################################################################')
        _print("%s:%d - show_stack_trace decorator\n\n" % (filename, lineno))
        sys.stdout.flush()
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stderr.flush()
        traceback.print_stack()
        sys.stderr.flush()
        sys.stderr.flush()
        _print('################################################################################')
        sys.stdout.flush()
        return func(*args, **kwargs)

    return wrapped_func


def print_stack_strace():
    traceback.print_stack()


def _show_caller(func):

    """
    function decorator to show caller of function, plus filename and lineno for decorator
    """

    def wrapped_func(*args, **kwargs):
        caller = getframeinfo(stack()[1][0])
        _print("%s:%d - %s" % (caller.filename, caller.lineno, func.__name__))
        return func(*args, **kwargs)

    return wrapped_func


@_show_caller
def show_print_caller():
    __print = builtins.print
    builtins._print = builtins.print

    def modified_print(*args, **kwargs):
        caller = getframeinfo(stack()[1][0])
        tmp = "%s:%d - print:" % (caller.filename, caller.lineno)
        return __print(tmp, *args, **kwargs)

    builtins.print = modified_print


@_show_caller
def hide_print_caller():
    try:
        builtins.print = builtins._print
    except AttributeError:
        return

    delattr(builtins, '_print')
