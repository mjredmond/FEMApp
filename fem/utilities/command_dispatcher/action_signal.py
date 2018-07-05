"""
command_dispatacher.action

Defines action signal

OSBSOLETE???

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

import os


version = os.environ.get('CommandDispatcherVersion', '1')

if version == '1':
    from ._command_dispatcher.action_signal import *
elif version == '2':
    from ._command_dispatcher_2.action_signal import *
elif version == '3':
    from ._command_dispatcher_3.action_signal import *
elif version == '4':
    from ._command_dispatcher_4.action_signal import *
