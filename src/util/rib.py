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
import collections
import sys

sys.path.insert(1, '..')
from route import Route


class RibIterator():
    """
    Iterator class for the RIB table object
    """

    def __init__(self, rt):
        """__init__.

        :param rt: table that need to be iterated on
        """
        self._rt = rt
        self._idx = 0

    def __next__(self):
        """
        Returns the next object for the RIB table
        """
        if self._idx < len(self._rt):
            key_result = self._rt.getKey(self._idx)
            result = self._rt[key_result]
            self._idx += 1
            return result

        raise StopIteration


class Rib(collections.MutableSequence):
    """Rib.
    Class used to handle the routing information base of a node
    """

    def __init__(self, node_id, logger):
        """__init__.

        :param node_id: id of the node that controls the rib object
        :param logger: logger object
        """
        self._table = {}
        self.oktype = Route
        self.id = node_id
        self.logger = logger

    def check(self, v):
        """check.

        :param v: check the type of v
        """
        if not isinstance(v, self.oktype):
            raise TypeError(v)

    def __len__(self): 
        """__len__."""
        return len(self._table)

    def __getitem__(self, i): 
        """__getitem__.

        :param i: key addr
        :return: route object of the first element in the list of routes that
        are contained in the table at the i key
        """
        if i in self._table:
            if len(self._table[i]) > 0:
                return self._table[i][0]
        return None

    def __delitem__(self, i): 
        """__delitem__.
        delete the first element in the list in the i reference of the table

        :param i: key
        """
        del self._table[i][0]

    def __setitem__(self, i, j, v):
        """__setitem__.

        :param i: table addres key
        :param j: vector element
        :param v: route to insert in position j of the vector in the i element
        of the table
        """
        self.check(v)
        self._table[i][j] = v

    def contains(self, i, v):
        """contains.
        check if the table contains the object v in the vector for the addr i

        :param i: addr key
        :param v: route to check
        """
        if i in self._table:
            if v in self._table[i]:
                return True
        return False

    def remove(self, i, v):
        """remove.
        remove object v from the vector of addr i if present

        :param i: addr key
        :param v: route that needs to be removed
        """
        if i in self._table:
            if v in self._table[i]:
                self._table[i].remove(v)
                return None
        return v

    def filter(self, route):
        """filter.
        filter function for routes before the introduction in the rib
        returns always true for now

        :param route: route that needs to be evaluated
        :return: True
        """
        return True

    def insert(self, i, v):
        """insert.
        Function to insert an object in the rib at the addr i

        :param i: key addr
        :param v: route to append
        """
        # Check v type
        self.check(v)
        # If the filter approves the route the add it
        if self.filter(v):
            # Check if it was already in the list
            if i not in self._table:
                self._table[i] = [v]
            elif v not in self._table[i]:
                self._table[i].append(v)
                # Sort the list for importance of the routes
                self._table[i] = sorted(self._table[i])
            # Log the new path to the destination
            self.logger.log_path(self.id, v)
            # Return the best route
            return self._table[i][0]
        # If it was not possible to enter the path then return None
        return None

    def getKey(self, i):
        """getKey.
        Return the ith key

        :param i: index
        """
        if i < len(self):
            return list(self._table.keys())[i]
        return None

    def __iter__(self):
        """__iter__."""
        return RibIterator(self)

    def __str__(self):
        """
        Function to return the RIB in a human readable format
        :returns: string with all the routing information
        """
        res = "RIB:\n"
        rt = sorted(self._table)
        for route in rt:
            res += str([str(x) for x in self._table[route]]) + "\n"
        return res
