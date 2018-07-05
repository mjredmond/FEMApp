from __future__ import print_function, absolute_import

from collections import OrderedDict
from six import iteritems

from fem.utilities import MrSignal
from fem.utilities.debug import show_stack_trace
from .selection_data import FemSelection


class FemGroup(FemSelection):
    def __init__(self):
        super(FemGroup, self).__init__()
        self.is_active = True
        self.group_name = ''

        self._member_list = ''
        self.data_changed.connect(self._update_list)

    def set_active(self, is_active=True):
        if is_active == self.is_active:
            return

        self.is_active = is_active
        self.data_changed.emit()

    def _update_list(self):
        self._member_list = super(FemGroup, self).to_str()

    def to_str(self):
        return self._member_list


class FemGroupList(object):
    def __init__(self):
        self.groups = OrderedDict()
        """:type: OrderedDict[FemGroup]"""

        self.data_changed = MrSignal()

        self._all_groups = FemGroup()

        self._default_group = FemGroup()
        self._default_group.group_name = 'Default'
        self._default_group.data_changed.connect(self._data_changed)

        self.groups['Default'] = self._default_group

    def _data_changed(self):
        self.all_groups()
        self.data_changed.emit()

    def add_group(self, name):
        if name == 'Default':
            self.groups['Default'] = self._default_group
            return self._default_group

        if name in self.groups:
            new_name = self.new_name()
            name = new_name.replace('group', name)

        new_group = FemGroup()
        new_group.data_changed.connect(self._data_changed)

        self.groups[name] = new_group
        new_group.group_name = name

        return new_group

    def remove_group(self, name):
        if name == 'Default':
            return

        try:
            old_group = self.groups[name]
            old_group.data_changed.disconnect(self._data_changed)
            del self.groups[name]
        except KeyError:
            pass

    def get_group(self, name):
        return self.groups[name]

    def get_group_by_index(self, index):
        group_name = list(self.groups.keys())[index]
        return self.groups[group_name]

    def rename_group(self, old_name, new_name):
        if old_name == 'Default':
            return

        if old_name not in self.groups:
            return

        group_names = list(self.groups.keys())

        tmp = dict(self.groups)

        self.groups.clear()

        for group_name in group_names:
            group = tmp[group_name]

            if group_name == old_name:
                group_name = new_name
                group.group_name = group_name

            self.groups[group_name] = group

        self.data_changed.emit()

    def set_active(self, group_name, bool):
        if group_name not in self.groups:
            return

        self.groups[group_name].set_active(bool)

    def show_group(self, name):
        try:
            self.groups[name].set_active(True)
        except KeyError:
            pass

    def hide_group(self, name):
        try:
            self.groups[name].set_active(False)
        except KeyError:
            pass

    def all_groups(self):

        data = self._all_groups

        data.data_changed.block()

        data.set_data([])

        add_data = data.data.add_data4

        for id, group in iteritems(self.groups):
            if group.is_active:
                add_data(group.data)

        data.data_changed.unblock()

        return data

    def size(self):
        return len(self.groups)

    def new_name(self):
        size = self.size()

        new_name_ = 'group_%d' % size

        while new_name_ in self.groups:
            size += 1
            new_name_ = 'group_%d' % size

        return new_name_

    def serialize(self):
        data = []

        for key, item in iteritems(self.groups):
            data.append((key, item.to_str()))

        return data

    def clear(self):
        self.groups.clear()

    def load(self, data):
        if not isinstance(data, list):
            return

        self.clear()

        for data_ in data:
            group_name, group_data = data_
            group = self.add_group(group_name)
            group.set_data(group_data)
