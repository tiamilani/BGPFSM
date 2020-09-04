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
import ast

from policies import PolicyValue

class Route():
    """Route
    Class to manage a single route
    """

    def __init__(self, addr, path, nh, mine=False, policy_value=PolicyValue(0)):
        """__init__.

        :param addr: addr of the route
        :param path: Path to reach the destination
        :param nh: Nh for the address
        :param policy_value: Policy value to associate with the route
        """
        self._addr = addr
        # Check that the path is an instance of a list
        if not isinstance(path, list):
            raise TypeError(path)
        self._path = path.copy()
        self._nh = nh
        
        # Check that the policy value is an object of class PolicyValue
        if not isinstance(policy_value, PolicyValue):
            raise TypeError(policy_value)

        self._mine = mine
        self._policy_value = policy_value

    @classmethod
    def fromString(cls, string):
        res = ast.literal_eval(string)
        return cls(ipaddress.ip_network(res["addr"]), 
                   res["path"], res["nh"],
                   policy_value = PolicyValue.fromString(res["policy_value"]))

    def add_to_path(self, value):
        """add_to_path.

        :param value: add a voice to the path list at the beginning
        """
        self.path.insert(0, value)

    def remove_from_path(self, value):
        """remove_from_path.

        :param value: remove a voice from the path
        """
        if value not in self.path:
            raise ValueError("object {} not in the path".format(value))
        self.path.remove(value)

    @property
    def addr(self):
        """addr."""
        return self._addr

    @property
    def path(self):
        """path."""
        return self._path

    @property
    def nh(self):
        """nh."""
        return self._nh

    @nh.setter
    def nh(self, value):
        """nh.

        :param value: set the Nh
        """
        self._nh = value

    @property
    def policy_value(self) -> PolicyValue:
        """policy_value.
        :return: the policy value associated with the route
        """
        return self._policy_value

    @policy_value.setter
    def policy_value(self, value: PolicyValue):
        """policy_value.

        :param value: Policy value to apply to the route
        :type value: PolicyValue
        """
        self._policy_value = value

    @property
    def mine(self):
        return self._mine

    def __lt__(self, route):
        """__lt__.

        :param route: route to compare with the self one
        """
        # Check policy
        if self.policy_value != route.policy_value:
            return self.policy_value < route.policy_value
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
        """__eq__.

        :param route: route to compare with the local one
        """
        NoneType = type(None)
        if not isinstance(self, NoneType) and \
            not isinstance(route, NoneType) and \
            self.addr == route.addr and \
            self.path == route.path and \
            self.nh == route.nh and \
            self.policy_value == route.policy_value:
                return True
        return False

    def __copy__(self):
        """__copy__."""
        return type(self)(self.addr, self.path, self.nh, 
                          policy_value=self.policy_value)

    def __deepcopy__(self, memo):
        """__deepcopy__.

        :param memo: things to copy
        """
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.addr, memo),
                deepcopy(self.path, memo),
                deepcopy(self.nh, memo),
                deepcopy(self.policy_value, memo))
            memo[id_self] = _copy
        return _copy

    def __str__(self):
        """__str__."""
        d = dict()
        d["addr"] = str(self.addr)
        d["nh"] = self.nh
        d["path"] = self.path
        d["policy_value"] = str(self.policy_value)
        return str(d)
