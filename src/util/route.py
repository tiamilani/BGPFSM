# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2020 Mattia Milani <mattia.milani@studenti.unitn.it>

import ipaddress
from copy import copy, deepcopy

class Route():
    """Route
    Class to manage a single route
    """

    def __init__(self, addr, path, nh):
        self._addr = addr
        if not isinstance(path, list):
            raise TypeError(path)
        self._path = path
        self._nh = nh

    def add_to_path(self, value):
        self.path.insert(0, value)

    def remove_from_path(self, value):
        self.path.remove(value)

    @property
    def addr(self):
        return self._addr

    @property
    def path(self):
        return self._path

    @property
    def nh(self):
        return self._nh

    @nh.setter
    def nh(self, value):
        self._nh = value

    def __lt__(self, route):
        # Check the path len
        if len(self.path) < len(route.path):
            return True
        elif len(self.path) == len(route.path):
            # Check the nh id
            if int(self.nh) < int(route.nh):
                return True
            elif self.nh == route.nh:
                # check the path without the first as
                actual = Route(self.addr, self.path[1:], self.path[1])
                new = Route(route.addr, route.path[1:], route.path[1])
                return actual < new
        return False

    def __eq__(self, route):
        NoneType = type(None)
        if not isinstance(self, NoneType) and \
            not isinstance(route, NoneType) and \
            self.addr == route.addr and \
            self.path == route.path and \
            self.nh == route.nh:
                return True
        return False

    def __copy__(self):
        return type(self)(self.addr, self.path, self.nh)

    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.addr, memo),
                deepcopy(self.path, memo),
                deepcopy(self.nh, memo))
            memo[id_self] = _copy
        return _copy

    def __str__(self):
        return "{}-{}-{}".format(self.addr, self.nh, self.path)
