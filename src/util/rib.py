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

"""
Rib module
==========

Control a routing information base
----------------------------------

Is possible to create and handle a routing information base using this module
It povides an iterable rib.
Is possible to register only routes in the rib.
New routes will be evaluated before the insertion.
A new route could override old routes from neighbours.

"""

import collections
import sys

sys.path.insert(1, '..')
from route import Route
from events import Events
from event import Event


class RibIterator(): # pylint: disable=too-few-public-methods
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
            key_result = self._rt.get_key(self._idx)
            result = self._rt[key_result]
            self._idx += 1
            return result

        raise StopIteration


class Rib(collections.MutableSequence): # pylint: disable=too-many-ancestors
    """Rib.
    Class used to handle the routing information base of a node
    """

    __ROUTE_COUNTER = 0

    def __init__(self, node_id, logger):
        """__init__.

        :param node_id: id of the node that controls the rib object
        :param logger: logger object
        """
        self._table = {}
        self.oktype = Route
        self.id = node_id # pylint: disable=invalid-name
        self.logger = logger
        self._support_route_identifier = {}
        self.actual_state = set()

    def check(self, value):
        """check.

        :param value: check the type of value
        """
        if not isinstance(value, self.oktype):
            raise TypeError(value)

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

    def __setitem__(self, i, j, v): # pylint: disable=unexpected-special-method-signature
        """__setitem__.

        :param i: table addres key
        :param j: vector element
        :param v: route to insert in position j of the vector in the i element
        of the table
        """
        self.check(v)
        self._table[i][j] = v

    def update_rib_state(self, route, event, insertion=True):
        """update_rib_state.
        Used to update the actual state of the rib after an update

        :param route: route removed or inserted
        :param event: Cause event
        :param insertion: (Default True) determine the type of update
        """
        # Concatenation of all route ids
        if insertion:
            if str(route) not in self._support_route_identifier.keys():
                self._support_route_identifier[str(route)] = self.__ROUTE_COUNTER
                self.__ROUTE_COUNTER += 1 # pylint: disable=invalid-name
            if self._support_route_identifier[str(route)] not in self.actual_state:
                self.actual_state.add(self._support_route_identifier[str(route)])
                if event is not None:
                    rib_change_event = Event(0, event.id, Events.RIB_CHANGE,
                                             None, None, obj=self.actual_state)
                else:
                    rib_change_event = Event(0, None, Events.RIB_CHANGE,
                                             None, None, obj=self.actual_state)

                self.logger.log_rib_change(self.id, rib_change_event)
        if not insertion:
            self.actual_state.remove(self._support_route_identifier[str(route)])
            # Log the state change
            if event is not None:
                rib_change_event = Event(0, event.id, Events.RIB_CHANGE,
                                         None, None, obj=self.actual_state)
            else:
                rib_change_event = Event(0, None, Events.RIB_CHANGE,
                                         None, None, obj=self.actual_state)
            self.logger.log_rib_change(self.id, rib_change_event)

    def contains(self, i, value):
        """contains.
        check if the table contains the object value in the vector for the addr i

        :param i: addr key
        :param value: route to check
        """
        if i in self._table:
            if value in self._table[i]:
                return True
        return False

    def remove(self, i, v, event=None): # pylint: disable=arguments-differ
        """remove.
        remove object v from the vector of addr i if present

        :param i: addr key
        :param v: route that needs to be removed
        """
        if i in self._table:
            if v in self._table[i]:
                self._table[i].remove(v)
                self.update_rib_state(v, event, insertion=False)
                return None
        return v

    def __loop_detection(self, route):
        if self.id in route.path:
            return False
        return True

    def filter(self, route):
        """filter.
        filter function for routes before the introduction in the rib
        returns always true for now

        :param route: route that needs to be evaluated
        :return: True
        """
        if not self.__loop_detection(route):
            return False
        return True

    def insert(self, i, v, event=None, implicit_withdraw=False): # pylint: disable=arguments-differ
        """insert.
        Function to insert an object in the rib at the addr i

        :param i: key addr
        :param v: route to append
        """
        # Check v type
        self.check(v)
        # If the filter approves the route then add it
        if self.filter(v):
            # Check if it was already in the list
            if i not in self._table:
                self._table[i] = [v]
            elif v not in self._table[i]:
                if implicit_withdraw:
                    for net in self._table[i]:
                        if net.nh == v.nh:
                            print("{}: Removing {} from rib".format(self.id, net))
                            self.actual_state.remove(self._support_route_identifier[str(net)])
                            self._table[i].remove(net)
                self._table[i].append(v)
                # Sort the list for importance of the routes
                self._table[i] = sorted(self._table[i])
            # Log the new path to the destination
            if event is not None:
                path_event = Event(0, event.id,  Events.RIB_CHANGE,
                                   None, None, obj=v)
            else:
                path_event = Event(0, None, Events.RIB_CHANGE, None, None, obj=v)
            self.logger.log_path(self.id, path_event)
            # Update the rib state
            self.update_rib_state(v, event)
            # Return the best route
            return self._table[i][0]
        # If it was not possible to enter the path then return None
        return None

    def get_key(self, i):
        """get_key.
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
        rib_table = sorted(self._table)
        for route in rib_table:
            res += str([str(x) for x in self._table[route]]) + "\n"
        return res
