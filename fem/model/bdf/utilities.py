from __future__ import print_function, absolute_import

import gc
import numpy as np
import struct
# noinspection PyUnresolvedReferences
from six.moves import range

from fem.utilities import debuginfo


def get_index_or_default(some_list, index, default, can_be_none=False):
    try:
        val = some_list[index]

        if can_be_none:
            return val

        if val is None:
            return default

        return val

    except IndexError:
        return default


def split_string(s, size):
    i1 = 0
    result = []
    while i1 < len(s):
        result.append(s[i1:(i1 + size)])
        i1 += size

    return result


def expand_list(text_list):
    parts = text_list.split(' ')

    result = []

    for part in parts:
        if part.replace(' ', '') == '':
            continue

        parts_ = part.split(':')
        try:
            first = int(parts_[0])
        except IndexError:
            first = int(parts_)
        except ValueError:
            debuginfo(text_list)
            debuginfo(part)
            debuginfo(parts_)
            raise

        try:
            last = int(parts_[1])
        except IndexError:
            last = first

        try:
            offset = int(parts_[2])
        except IndexError:
            offset = 1

        for id_ in range(first, last + offset, offset):
            result.append(id_)

    return result


def condense_list(some_list):

    some_list = sorted(set(some_list))

    if len(some_list) < 2:
        try:
            return str(some_list[0])
        except IndexError:
            return ""

    results = ""

    first = some_list[0]
    second = 0
    count = 0

    for i in range(1, len(some_list)):
        count += 1
        second = some_list[i]

        if second - first != count:
            tmp = some_list[i-1]
            if first != tmp:
                if tmp - first == 1:
                    results += "%d %d "% (first, tmp)
                else:
                    results += "%d:%d " % (first, tmp)
            else:
                results += "%d " % first
            first = second
            count = 0

    if count != 0:
        if first != second:
            if second - first == 1:
                results += "%d %d " % (first, second)
            else:
                results += "%d:%d " % (first, second)
        else:
            results += "%d " % first

    last = str(some_list[-1])

    results = results[:-1]

    if not results.endswith(last):
        results = results + " " + last

    return results


def nearest_node_loc_approx(bulk_data, eid, node_list, ref_coord=None):
    distance = []

    if ref_coord is None:
        x0, y0, z0 = bulk_data['ELEMENT'][eid].get_ref_coord()[0]
    else:
        x0, y0, z0 = ref_coord

    grids = bulk_data['GRID']

    for i in range(len(node_list)):
        nid = node_list[i]
        x, y, z = grids[nid].to_global()
        dist = (x0 - x) ** 2 + (y0 - y) ** 2 + (z0 - z) ** 2
        distance.append([nid, dist])

    #for nid in node_list:
    #    try:
    #        x, y, z = grids[nid].to_global()
    #    except TypeError:
    #        print node_list
    #        print nid
    #        raise
    #    dist = (x0 - x) ** 2 + (y0 - y) ** 2 + (z0 - z) ** 2
    #    distance.append([nid, dist])

    sorted_distance = sorted(distance, key=lambda l: l[1])

    dist1 = sorted_distance[0][1]
    node1 = np.array(grids[sorted_distance[0][0]].to_global(), dtype='float64')

    try:
        dist2 = sorted_distance[1][1]
        node2 = np.array(grids[sorted_distance[1][0]].to_global(), dtype='float64')
    except IndexError:
        dist2 = dist1
        node2 = node1

    p01, p02, p03 = x0, y0, z0
    p11, p12, p13 = node1
    p21, p22, p23 = node2

    m = -((p13 - p03) * p23 + (p12 - p02) * p22 +
          (p11 - p01) * p21 - p13 * p13 + p03 * p13 - p12 * p12 + p02 * p12 - p11 * p11 + p01 * p11) / \
        (p23 * p23 - 2. * p13 * p23 + p22 * p22 - 2. * p12 * p22 +
         p21 * p21 - 2. * p11 * p21 + p13 * p13 + p12 * p12 + p11 * p11)

    distance = dist1 + (dist2 - dist1)*m

    return node1 + (node2 - node1) * m, distance


def rotate_vector_about_axis(vector, axis, theta):
    from math import sqrt, cos, sin

    theta = np.asarray(theta)

    axis /= sqrt(np.dot(axis, axis))
    a = cos(theta / 2.)
    b, c, d = -axis * sin(theta / 2.)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d

    rotation_matrix = np.array([[aa + bb - cc - dd, 2. * (bc + ad), 2. * (bd - ac)],
                                [2. * (bc - ad), aa + cc - bb - dd, 2. * (cd + ab)],
                                [2. * (bd + ac), 2. * (cd - ab), aa + dd - bb - cc]])

    return np.dot(rotation_matrix, vector)


def unravel_list(some_list):
    if not some_list:
        return []

    result = []
    if isinstance(some_list[0], list):
        for i in range(len(some_list)):
            result.extend(unravel_list(some_list[i]))
    else:
        for i in range(len(some_list)):
            result.append(some_list[i])

    return result


def align_element_material_system_with_nodes(bulk_data, elements_list, nodes_list):
    if isinstance(elements_list, str):
        elements_list = expand_list(elements_list)

    if isinstance(nodes_list, str):
        nodes_list = expand_list(nodes_list)

    elements = bulk_data['ELEMENT']

    nodes_list_ = unravel_list(nodes_list)

    count = 0

    for eid in elements_list:
        loc, dist = nearest_node_loc_approx(bulk_data, eid, nodes_list_)

        element = elements[eid]

        #print eid, nearest_loc
        element.set_point_on_material_y(loc)


def align_cbush_coordinate_system_with_nodes(bulk_data, elements_list, nodes_list, cord2r_offset):
    if isinstance(elements_list, str):
        elements_list = expand_list(elements_list)

    if isinstance(nodes_list, str):
        nodes_list = expand_list(nodes_list)

    nodes_list_ = unravel_list(nodes_list)

    elements = bulk_data['ELEMENT']

    for eid in elements_list:
        element = elements[eid]
        nearest_loc, dist = nearest_node_loc_approx(bulk_data, eid, nodes_list_, element._ga.to_global())

        element.set_point_on_y(nearest_loc, cord2r_offset)


def format_float_data(card_data, card_len=16):
    if not isinstance(card_data, float):
        card_data = float(card_data)

    if card_data > 0.:
        prefix = ''
    else:
        prefix = '-'
        card_len -= 1

    card_data = abs(card_data)

    card_txt = str(card_data)

    while card_txt[0] == '0':
        card_txt = card_txt[1:]

    while card_txt[-1] == '0':
        card_txt = card_txt[:-1]

    if len(card_txt) <= card_len:
        if prefix != '':
            fmt = "%" + "%ds" % (card_len+1)
        else:
            fmt = "%" + "%ds" % card_len

        result = prefix + card_txt.strip()

        if result == '.' or result == '-.':
            result = '.0'

        return fmt % result

    from math import log10
    exponent = int(log10(card_data))

    if exponent > 0.:
        exponent = "+" + str(exponent)
    else:
        exponent = str(exponent)

    remaining_width = card_len - len(exponent)

    tmp = card_txt.split('.')
    no_decimals = tmp[0] + tmp[1]

    if card_data >= 1.:
        before_decimal = no_decimals[0] + '.'
        after_decimal = no_decimals[1:]
    else:
        before_decimal = '.'
        after_decimal = no_decimals

    remaining_width -= len(before_decimal)

    after_decimal = after_decimal[:remaining_width]

    return prefix + before_decimal + after_decimal + exponent


def format_data(card_data, card_len=16):
    if isinstance(card_data, str):
        fmt = "%" + "%ds" % card_len
        return fmt % card_data.strip()
    elif isinstance(card_data, int):
        fmt = "%" + "%dd" % card_len
        return fmt % card_data
    elif isinstance(card_data, float):
        return format_float_data(card_data, card_len)
    elif card_data is None:
        return ' '*card_len
    else:
        debuginfo(card_data)
        raise Exception


def data_from_buffer2(buffer):
    buffer_size = len(buffer)

    print(buffer[:100])

    i = 0

    data = []

    unpack = struct.unpack

    while i < buffer_size:

        data_type = buffer[i]

        print(data_type)

        if data_type == 'x':
            # None
            data.append(None)
            i += 1

        elif data_type == 's':
            # string
            i += 1
            str_len = unpack('i', buffer[i:(i+4)])[0]
            i += 4
            data.append(buffer[i:(i+str_len)])
            i += str_len

        elif data_type == 'i':
            # int
            i += 1
            data.append(unpack('i', buffer[i:(i+4)])[0])
            i += 4

        elif data_type == 'q':
            # long
            i += 1
            data.append(unpack('q', buffer[i:(i+8)])[0])
            i += 8

        elif data_type == 'f':
            # float
            i += 1
            data.append(unpack('f', buffer[i:(i+4)])[0])
            i += 4

        elif data_type == 'd':
            # double
            i += 1
            data.append(unpack('d', buffer[i:(i+8)])[0])
            i += 8

        elif data_type == '\0':
            # null
            i += 1
            data.append('\0')

        else:
            raise ValueError(data_type)

    return data


if __name__ == '__main__':
    buffer = data_to_buffer("abcdefg", 7, 1.23435, None, "asdfaskdf;askf", -5, 4.56454)

    debuginfo(len(buffer))

    # 1 + 4 + 7 + 1 + 4 + 1 + 8 + 1 + 4 + 1 + 8 + 1 + 1 + 4

    debuginfo(data_from_buffer(buffer))
