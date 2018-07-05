"""
command_dispatacher.command_dispatcher

Defines command dispatcher

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

import os


version = os.environ.get('CommandDispatcherVersion', '1')

if version == '1':
    from ._command_dispatcher.command_dispatcher import *
elif version == '2':
    from ._command_dispatcher_2.command_dispatcher import *
elif version == '3':
    from ._command_dispatcher_3.command_dispatcher import *
elif version == '4':
    from ._command_dispatcher_4.command_dispatcher import *
    from ._command_dispatcher_4.command_dispatcher_wrapper import *
