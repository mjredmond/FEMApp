"""
command_dispatacher

Dispatches commands

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from .command_dispatcher import *
from .action import *
from .command import *

import os

dispatcher_version = os.environ.get('CommandDispatcherVersion', '1')

del os
