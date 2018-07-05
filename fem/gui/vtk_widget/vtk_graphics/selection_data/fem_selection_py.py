from __future__ import print_function, absolute_import

import numpy as np
from typing import List, Set


class FemSelection(object):
    def __init__(self):
        self._data = set()  # type: Set[int]

    def clear(self):
        self._data.clear()

    def set_data1(self, data):
        # type: (int)->None
        self._data.clear()
        self._data.add(data)

    def set_data2(self, data):
        # type: (List[int])->None
        self._data.clear()
        self._data.update(set(data))

    def set_data3(self, data):
        # type: (Set[int])->None
        self._data.clear()
        self._data.update(data)

    def set_data4(self, data, data_size):
        # type: (List[int], int)->None
        self._data.clear()
        self._data.update(set(data[:data_size]))

    def add_data1(self, data):
        # type: (int)->None
        self._data.add(data)

    def add_data2(self, data):
        # type: (List[int])->None
        self._data.update(set(data))

    def add_data3(self, data):
        # type: (Set[int])->None
        self._data.update(data)

    def add_data4(self, data):
        # type: (FemSelection)->None
        self._data.update(data._data)

    def remove_data1(self, data):
        # type: (int)->None
        self._data.discard(data)

    def remove_data2(self, data):
        # type: (List[int])->None
        self._data.symmetric_difference_update(set(data))

    def remove_data3(self, data):
        # type: (Set[int])->None
        self._data.symmetric_difference_update(data)

    def intersect1(self, data):
        # type: (int)->None
        self._data.insersection_update(set([data]))

    def intersect2(self, data):
        # type: (List[int])->None
        self._data.insersection_update(set(data))

    def intersect3(self, data):
        # type: (Set[int])->None
        self._data.insersection_update(data)

    def contains(self, data):
        # type: (int)->bool
        return data in self._data

    def condense(self):
        # type: ()->List[List[int]]
        vec = self.to_vector()
        if vec.size <= 2:
            return [vec.tolist()]

        first = vec[0]
        second = 0
        count = 0

        old_category = int(first / 100000000)
        category = 0
        offset = 0

        results = []

        tmp = []

        for i in range(1, vec.size):
            count += 1
            second = vec[i]

            category = int(second / 100000000)

            if category != old_category:
                results.append([])
                first = second
                second = 0
                count = 0
                offset = 0
                old_category = category
                continue

            if offset == 0:
                offset = second - first

            if second - first != count:
                tmp_ = vec[i-1]
                if first != tmp_:
                    if tmp_ - first == offset:
                        tmp.extend([first, -1, -1])
                        tmp.extend([tmp_, -1, -1])
                    else:
                        offset_ = -1
                        if offset > 1:
                            offset_ = offset
                        tmp.extend([first, tmp_, offset_])
                else:
                    tmp.append([first, -1, -1])

                first = second
                count = 0

        if count != 0:
            if first != second:
                if second - first == offset:
                    tmp.extend([first, -1, -1])
                    tmp.extend([second, -1, -1])
                else:
                    offset_ = -1
                    if offset > 1:
                        offset_ = offset
                    tmp.extend([first, second, offset_])

        sz = len(tmp)

        if sz > 3 and tmp[sz-1] == tmp[sz-4] and tmp[sz-2] == tmp[sz-5] and tmp[sz-3] == tmp[sz-6]:
            tmp = tmp[:sz-3]

        sz = len(tmp)
        if sz > 0:
            results.append(tmp)

        return results

    def raw_pointer(self):
        # type: ()->None
        return self

    def to_vector(self):
        # type: ()->List[int]
        return np.array(sorted(self._data))

    def selection_by_category(self, category):
        # type: (int)->List[int]
        result = []

        for i in self._data:
            _category = int(i / 100000000)
            if _category == category:
                result.append(i)

        return result

    def __contains__(self, data):
        return data in self._data
