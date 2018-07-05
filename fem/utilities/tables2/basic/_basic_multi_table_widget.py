from ..abstract import AbstractMultiTableWidget

from ._basic_table_widget import BasicTableWidget


class BasicMultiTableWidget(AbstractMultiTableWidget):
    TableWidget = BasicTableWidget

