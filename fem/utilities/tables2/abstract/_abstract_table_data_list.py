

class AbstractTableDataList(object):
    CheckDataType = None
    DefaultDataType = None

    MultiTableWidget = None
    
    def __init__(self):
        self.model = None
        self.data = []

        from ._abstract_multi_table_widget import AbstractMultiTableWidget
        self.MultiTableWidget = AbstractMultiTableWidget
        
    def register_model(self, model):
        self.model = model
        
        for data in self.data:
            data.register_model(model)

    def clear(self):
        raise NotImplementedError

    def get_id(self):
        raise NotImplementedError

    @property
    def headers(self):
        raise NotImplementedError
    
    @property
    def formats(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def load_data(self, data):
        raise NotImplementedError

    def add(self, *data):
        raise NotImplementedError

    def remove(self, index):
        raise NotImplementedError

    def remove_multiple(self, indices):
        raise NotImplementedError

    def insert(self, index, *data):
        raise NotImplementedError

    def insert_multiple(self, indices):
        raise NotImplementedError

    def shape(self):
        raise NotImplementedError

    def editable_columns(self):
        raise NotImplementedError

    def set_data(self, index, value):
        raise NotImplementedError

    def validate(self, *args):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError

    def load(self, data):
        raise NotImplementedError

    def up(self, index):
        raise NotImplementedError

    def down(self, index):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, index):
        raise NotImplementedError

    def __setitem__(self, index, data):
        raise NotImplementedError

    def id_exists(self, id_):
        for data in self.data:
            if id_ == data.get_id():
                return True
            
        return False

    def subdata(self, index):
        raise NotImplementedError

    def has_subdata(self):
        raise NotImplementedError

    def find_index(self, data_id):
        for i in range(len(self.data)):
            if self.data[i].get_id() == data_id:
                return i
        
        return -1

    def get_index(self, data):
        for i in range(len(self.data)):
            if self.data[i] is data:
                return i

        return -1

    def ids(self):
        return [_.get_id() for _ in self.data]

    @property
    def size(self):
        return len(self.data)
    
    def resize(self, new_size):
        raise NotImplementedError
    
    @property
    def resizable(self):
        return True
    
    def get_formatted_data_by_index(self, index):
        row, col = index
        try:
            return self.data[row].get_formatted_data(col)
        except IndexError:
            print(self.data)
            raise

    def get_edit_data_by_index(self, index):
        row, col = index
        return self.data[row].get_edit_data(col)
    
    def ui_edit(self):

        import sys

        # for some reason PyQt5 prevents tracebacks from showing unless an exception hook is set
        def app_exception_hook(type_, value_, tback_):
            sys.__excepthook__(type_, value_, tback_)

        old_excepthook = sys.excepthook

        sys.excepthook = app_exception_hook

        from qtpy import QtCore, QtWidgets
        
        app = QtWidgets.QApplication.instance()
        
        if app is None:
            app = QtWidgets.QApplication([])
            
        w = self.MultiTableWidget()
        w.set_model_data(self)
        w.show()
        
        app.exec_()

        sys.excepthook = old_excepthook

