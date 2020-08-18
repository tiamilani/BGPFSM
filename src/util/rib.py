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
    Iterator class for the routing table object
    """

    def __init__(self, rt):
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


class Rib(collections.MutableSequence):
    """Rib.
    Class used to handle the routing information base of a node
    """

    def __init__(self):
        self._table = {}
        self.oktype = Route

    def check(self, v):
        if not isinstance(v, self.oktype):
            raise TypeError(v)

    def __len__(self): 
        return len(self._table)

    def __getitem__(self, i): 
        if i in self._table:
            return self._table[i][0]
        else:
            return None

    def __delitem__(self, i): 
        del self._table[i][0]

    def __setitem__(self, i, j, v):
        self.check(v)
        self._table[i][j] = v

    def filter(self, route):
        return True

    def insert(self, i, v):
        self.check(v)
        if i not in self._table:
            self._table[i] = [v]
            return self._table[i][0]
        else:
            if self.filter(v):
                self._table[i].append(v)
                self._table[i] = sorted(self._table[i])
                return self._table[i][0]
        return None

    def getKey(self, i):
        if i < len(self):
            return list(self._table.keys())[i]
        return None

    def __iter__(self):
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
