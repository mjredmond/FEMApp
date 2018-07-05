"""
command_dispatacher.undo_stack

Defines undo stack

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

import os


version = os.environ.get('CommandDispatcherVersion', '1')

if version == '1':
    from ._command_dispatcher.undo_stack import *
elif version == '2':
    from ._command_dispatcher_2.undo_stack import *
elif version == '3':
    from ._command_dispatcher_3.undo_stack import *
elif version == '4':
    from ._command_dispatcher_4.undo_stack import *