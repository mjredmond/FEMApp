"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import

from fem.utilities.tables.table_data import TableDataList


class MainData(TableDataList):
    def validate(self, *args):
        return True
