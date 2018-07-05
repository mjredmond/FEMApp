

class AbstractTableData(object):
    headers = []
    formats = []
    setters = []
    getters = []
    
    def __init__(self):
        self.model = None
        self.parent = None
        self.set_data = self.__setitem__

        self._setters = [getattr(self, attr) for attr in self.setters]
        self._getters = [getattr(self, attr) for attr in self.getters]
        
        self._id = ''
        
    def register_model(self, model):
        self.model = model
        
    def register_parent(self, parent):
        self.parent = parent

    def __getitem__(self, index):
        return self._getters[index]()

    def __setitem__(self, index, value):
        self._setters[index](value)

    def __len__(self):
        return len(self.headers)

    @property
    def id(self):
        return self.get_id()

    @id.setter
    def id(self, value):
        self.set_id(value)

    def serialize(self):
        return [getter() for getter in self._getters]

    def load(self, data):
        # load from serialization
        for i in range(len(data)):
            self._setters[i](data[i])

    def subdata(self, index):
        raise NotImplementedError

    def get_id(self):
        return self._id
    
    def set_id(self, value):
        value = str(value)
        
        if value in self.parent.ids():
            return
        
        self._id = value
    
    def get_edit_data(self, index):
        return str(self[index])
    
    def get_formatted_data(self, index):
        formatter = self.formats[index]
        
        if isinstance(formatter, str):
            return formatter % self[index]
        
        return formatter(self[index])

