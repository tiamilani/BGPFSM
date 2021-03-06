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

# pylint: disable=invalid-name

"""
RoutingTable module
===================

Manage the routing table
------------------------

Is possible to create a routing table and manage it, it can contains
only one route per address

"""

import collections
import sys

sys.path.insert(1, '..')
from route import Route


class RoutingTableIterator(): # pylint: disable=too-few-public-methods
    """
    Iterator class for the routing table object
    """

    def __init__(self, rt):
        """__init__.

        :param rt:
        """
        self._rt = rt
        self._idx = 0

    def __next__(self):
        """
        Returns the next object for the routing table
        """
        if self._idx < len(self._rt):
            key_result = self._rt.getKey(self._idx)
            result = self._rt[key_result]
            self._idx += 1
            return result

        raise StopIteration


class RoutingTable(collections.MutableSequence): # pylint: disable=too-many-ancestors
    """RoutingTable.
    Class used to handle the routing table of a node
    """

    def __init__(self):
        """__init__."""
        self._table = {}
        self.oktype = Route

    def check(self, value):
        """check.

        :param value: check that V is a route instance
        """
        if not isinstance(value, self.oktype):
            raise TypeError(value)

    def __len__(self):
        """__len__."""
        return len(self._table)

    def __getitem__(self, i):
        """__getitem__.

        :param i: key addr
        """
        if i in self._table:
            return self._table[i]
        return None

    def __delitem__(self, i):
        """__delitem__.

        :param i: key addr
        """
        if i in self._table:
            del self._table[i]

    def __setitem__(self, i, v):
        """__setitem__.

        :param i: key addr
        :param v: route
        """
        self.check(v)
        self._table[i] = v

    def insert(self, i, v): # pylint: disable=arguments-differ
        """insert.
        Is not possible to insert any route in the Routing Table
        This method has no effects

        :param i:
        :param v:
        """

    def getKey(self, i): # pylint: disable=invalid-name
        """getKey.

        :param i: index
        """
        if i < len(self):
            return list(self._table.keys())[i]
        return None

    def __iter__(self):
        """__iter__."""
        return RoutingTableIterator(self)

    def __str__(self):
        """
        Function to return the routing table in a human readable format
        :returns: string with all the routing information
        """
        res = "Routing Table:\n"
        routing_table = sorted(self._table)
        for route in routing_table:
            res += str(self._table[route]) + "\n"
        return res
