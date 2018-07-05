from __future__ import print_function, absolute_import

from . import (file)
from ..configuration import config

config.dispatcher.verify()
del config
