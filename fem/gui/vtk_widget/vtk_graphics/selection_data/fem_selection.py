from __future__ import print_function, absolute_import

import numpy as np

from fem.utilities import MrSignal
from fem.model.bdf.card_info_list import CardInfoList
from fem.model.bdf.utilities import expand_list, condense_list
from .fem_selection_py import FemSelection as FemSelectionCpp

bdf_card_info = CardInfoList.instance()
""":type: CardInfoList"""

from collections import OrderedDict

import re

from six import iteritems, integer_types

integer_type = integer_types[0]


class FemSelection(object):
    def __init__(self):
        self.data = FemSelectionCpp()
        self.data_changed = MrSignal()

    def clear(self):
        self.data.clear()

    def copy(self, other):
        """

        :param other:
        :type other: FemSelection
        :return:
        :rtype:
        """
        self.set_data(other.data._data)

    def set_data(self, data):
        if isinstance(data, int):
            self.data.set_data1(data)
        elif isinstance(data, list):
            self.data.set_data2(data)
        elif isinstance(data, set):
            self.data.set_data3(data)
        elif isinstance(data, np.ndarray):
            self.data.set_data4(data, data.size)
        elif isinstance(data, str):
            self.data.set_data2(self.from_str(data))
        else:
            raise TypeError(type(data))

        self.data_changed.emit()

    def add_data(self, data):
        if isinstance(data, int):
            self.data.add_data1(data)
        elif isinstance(data, list):
            self.data.add_data2(data)
        elif isinstance(data, set):
            self.data.add_data3(data)
        elif isinstance(data, np.ndarray):
            self.data.add_data2(data)
        elif isinstance(data, str):
            self.data.add_data2(self.from_str(data))
        else:
            raise TypeError(type(data))

        self.data_changed.emit()

    def intersect(self, data):
        if isinstance(data, int):
            self.data.intersect1(data)
        elif isinstance(data, list):
            self.data.intersect2(data)
        elif isinstance(data, set):
            self.data.intersect3(data)
        elif isinstance(data, np.ndarray):
            self.data.intersect2(data)
        elif isinstance(data, str):
            self.data.intersect2(self.from_str(data))
        else:
            raise TypeError(type(data))

        self.data_changed.emit()

    def remove_data(self, data):
        if isinstance(data, int):
            self.data.remove_data1(data)
        elif isinstance(data, list):
            self.data.remove_data2(data)
        elif isinstance(data, set):
            self.data.remove_data3(data)
        elif isinstance(data, np.ndarray):
            self.data.remove_data2(data)
        elif isinstance(data, str):
            self.data.remove_data2(self.from_str(data))
        else:
            raise TypeError(type(data))

        self.data_changed.emit()

    def to_set(self):
        return self.data._data

    def to_numpy(self):
        return self.data.to_vector()

    def to_vector(self):
        return self.data.to_vector()

    def selection_by_category(self, category):
        results = self.data.selection_by_category(category)
        tmp = FemSelection()
        tmp.set_data(results)

        return tmp

    def to_str(self):
        sorted_list = sorted(list(self.data.to_vector()))

        categories = OrderedDict()

        get_category = bdf_card_info.card_category_by_eid
        global_id = bdf_card_info.global_id

        for eid in sorted_list:
            category = get_category(eid)
            eid_ = global_id(eid)
            try:
                categories[category].append(eid_)
            except KeyError:
                categories[category] = [eid_]

        result = ""

        for category, the_list in iteritems(categories):
            result += "%s %s\n\n" % (str(category), condense_list(the_list))

        return result[:-1]

    def to_str2(self):
        condensed = self.data.condense()

        get_category = bdf_card_info.card_category_by_eid
        global_id = bdf_card_info.global_id

        result = []

        # FIXME: fix for len(condensed) < 3
        # FIXME: this method doesn't work

        for tmp in condensed:

            try:
                category = get_category(tmp[0]).decode('utf-8')
            except IndexError:
                continue

            tmp_result = [category]

            for i in range(0, len(tmp), 3):
                eid1 = tmp[i]
                eid2 = tmp[i+1]
                stride = tmp[i+2]

                if stride != -1:
                    eid1 = global_id(eid1)
                    eid2 = global_id(eid2)
                    tmp_result.append('%d:%d:%d' % (eid1, eid2, stride))
                elif eid2 != -1:
                    eid1 = global_id(eid1)
                    eid2 = global_id(eid2)
                    tmp_result.append('%d:%d' % (eid1, eid2))
                else:
                    tmp_result.append('%d' % global_id(eid1))

            if len(tmp_result) > 1:
                result.append(' '.join(tmp_result))

        return '\n\n'.join(result)

    def from_str(self, data):
        if data == "":
            return []

        data_ = re.split(' |\n', data)

        def get_category(data):
            try:
                first = data[0].upper()
            except IndexError:
                return None

            if "G" == first or "N" == first:
                return "GRID"
            elif "E" == first:
                return "ELEMENT"
            elif "P" == first:
                return "PROPERTY"
            elif "R" == first:
                return "RBE"
            elif "M" == first:
                return "MPC"
            elif "F" == first:
                return "FORCE"
            elif "D" == first:
                return "Disp"
            elif "C" == first:
                return "COORD"
            else:
                return None

        results_ = []
        offset = 0

        for dat_ in data_:
            category = get_category(dat_)
            if category is not None:
                offset = bdf_card_info.categories(category) * 100000000
                continue

            new_list = [i + offset for i in expand_list(dat_)]
            results_.extend(new_list)

        return results_

    def set_from_str(self, data):
        self.set_data(self.from_str(data))
        return self

    def raw_pointer(self):
        return self.data._data

    def __iand__(self, data):
        self.intersect(data)
        return self

    def __ior__(self, data):
        self.add_data(data)
        return self

    def __contains__(self, data):
        return self.data.contains(data)


if __name__ == '__main__':
    selection = FemSelection()
    selection.set_from_str("Node 1 2 3 4 Elem 5 6 7 8")
    print(selection.to_str())



#a = FemSelection()

#print a.selection_data.raw_pointer()
#print a.raw_pointer()

#a.add_data(1)
#a.add_data(2)
#a.add_data([5, 6, 7])
#a.add_data([102342343, 202342343, 102342345])
#a.add_data([100000000+561452])

#print a.to_str()

#a.add_data("Elem 561452 894521 1023:1028")

#a.add_data("Node 500:510")

#print a.to_str()

#b = set([7, 2, 9, 11])

#a |= b

#print a.to_set()

#print a.to_numpy()

#print type(arr)
