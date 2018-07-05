from ..abstract import AbstractTableView

from ._basic_table_model import BasicTableModel


class BasicTableView(AbstractTableView):
    TableModel = BasicTableModel
