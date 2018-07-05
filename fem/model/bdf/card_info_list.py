from __future__ import print_function, absolute_import

from typing import Dict, List


class CardInfo(object):
    _index = 0

    def __init__(self, card_id, category, dimensions):
        self.id = card_id
        self.category = category
        self.index = self._index
        self.dimensions = dimensions
        self.__class__._index += 1


class CardInfoList(object):
    _instance = None

    data = {}  # type: Dict[str, CardInfo]
    bdf_categories = ['GRID', 'ELEMENT', 'PROPERTY', 'RBE', 'MPC', 'FORCE', 'DISP', 'COORD']
    to_fem_type = {
        'GRID': 'Node', 'ELEMENT': 'Elem', 'EL': 'Elem', 'ELEM': 'Elem', 'PROPERTY': 'Prop', 'PROP': 'Prop',
        'RBE': 'RBE', 'MPC': 'MPC', 'FORCE': 'Force', 'DISP': 'Disp', 'COORD': 'Coord', 'CORD': 'Coord'
    }
    _categories = {}  # type: Dict[str, int]

    for i in range(len(bdf_categories)):
        _categories[bdf_categories[i]] = i

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CardInfoList, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def add_data(self, name, obj):
        self.data[name] = obj

    def get_data(self, name):
        return self.data[name]

    def card_category_by_index(self, index):
        return self.bdf_categories[index]

    def card_category_by_eid(self, eid):
        return self.bdf_categories[int(eid / 100000000)]

    def global_id(self, eid):
        return eid - 100000000 * int(eid / 100000000)

    def from_global_id(self, eid, category):
        return eid + 100000000 * category

    def categories(self, category):
        if isinstance(category, str):
            return self._categories[category]
        elif isinstance(category, int):
            return self.bdf_categories[category]

        raise TypeError(type(category))

    def all_fem(self):
        tmp = {'ELEMENT', 'GRID', 'MPC', 'RBE'}
        results = []

        for obj in self.data.values():
            if obj.category in tmp:
                results.append(obj.index)

        return results

    def _get_fem_by_category(self, category, dims):
        results = []
        for obj in self.data.values():
            if obj.category in category and obj.dimensions == dims:
                results.append(obj.index)

        return results

    def point_fem(self):
        return self._get_fem_by_category({'ELEMENT'}, 0)

    def line_fem(self):
        return self._get_fem_by_category({'ELEMENT'}, 1)

    def shell_fem(self):
        return self._get_fem_by_category({'ELEMENT'}, 2)

    def solid_fem(self):
        return self._get_fem_by_category({'ELEMENT'}, 3)

    def _get_fem_by_id(self, ids):
        results = []
        for obj in self.data.values():
            if obj.id in ids:
                results.append(obj.index)

        return results

    def tri_fem(self):
        return self._get_fem_by_id({'CTRIA3', 'CTRIA6', 'CTRIAR', 'CTRIAX', 'CTRIAX6'})

    def quad_fem(self):
        return self._get_fem_by_id({'CSHEAR', 'CQUAD', 'CQUAD4', 'CQUAD8', 'CQUADR', 'CQUADX'})

    def grid_fem(self):
        return self._get_fem_by_id({'GRID'})

    def mpc_fem(self):
        return self._get_fem_by_id({'MPC'})

    def coord_fem(self):
        return self._get_fem_by_id({'COORD'})


########################################################################################################################

import os
card_info = os.path.join(os.path.dirname(__file__), 'card_info.txt')
with open(card_info, 'r') as f:
    lines = f.read().split('\n')
    for line in lines:
        if line == '':
            break
        tmp = line.split(',')
        CardInfoList.data[tmp[0]] = CardInfo(tmp[0], tmp[1], int(tmp[2]))


del os
del card_info
