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

    def __init__(self, rib):
        """__init__.

        :param rt: table that need to be iterated on
        """
        self._rib = rib
        self._idx = 0

    def __next__(self):
        """
        Returns the next object for the RIB table
        """
        if self._idx < len(self._rib):
            key_result = self._rib.get_key(self._idx)
            result = self._rib[key_result]
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

class BaseRib(collections.MutableSequence): # pylint: disable=too-many-ancestors
    """Rib.
    Class used to handle the routing information base of a node
    """

    def __init__(self):
        """__init__.
        """

        self._destinations = {}

    def __len__(self):
        """__len__."""
        return len(self._destinations)

    def __getitem__(self, i):
        """__getitem__.

        :param i: key addr
        :return: route object of the first element in the list of routes that
        are contained in the table at the i key
        """
        i = hash(i.addr)
        if i in self._destinations:
            return self._destinations[i]
        else:
            raise KeyError("{} key not found in the RIB".format(i))

    def __delitem__(self, i):
        """__delitem__.
        delete the first element in the list in the i reference of the table

        :param i: key
        """
        i = hash(i.addr)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        del self._destinations[i]

    def __setitem__(self, i, v): # pylint: disable=unexpected-special-method-signature
        """__setitem__.

        :param i: table addres key
        :param v: route to insert in position j of the vector in the i element
        of the table
        """
        i = hash(i.addr)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        self._destinations[i] = v

    def contains(self, i, value):
        """contains.
        check if the table contains the object value in the vector for the addr i

        :param i: addr key
        :param value: route to check
        """
        i = hash(i)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        if value in self._destinations[i]:
            return True
        return False

    def remove(self, v): # pylint: disable=arguments-differ
        """remove.
        remove object v from the vector of addr i if present

        :param i: addr key
        :param v: route that needs to be removed
        """
        i = hash(v.addr)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        if v in self._destinations[i]:
            self._destinations[i].remove(v)
            return None
        return v

    def insert(self, v): # pylint: disable=arguments-differ
        """insert.
        Function to insert an object in the rib at the addr i

        :param i: key addr
        :param v: route to append
        """
        # Check if it was already in the list
        i = hash(v.addr)
        if i not in self._destinations:
            self._destinations[i] = [v]
        elif v not in self._destinations[i]:
            self._destinations[i].append(v)
        else:
            # If it was not possible to enter the path then return None
            return None
        return v

    def keys(self):
        return self._destinations.keys()
    
    def exists(self, destination):
        i = hash(destination.addr)
        return i in self.keys()

    def get_key(self, i):
        """get_key.
        Return the ith key

        :param i: index
        """
        if i < len(self._destinations):
            return self._destinations[list(self._destinations.keys())[i]][0]
        return None

    def __iter__(self):
        """__iter__."""
        return RibIterator(self)

    def __str__(self):
        """
        Function to return the RIB in a human readable format
        :returns: string with all the routing information
        """
        dest_table = sorted(self._destinations)
        res = ""
        for route in dest_table:
            res += str([str(x) for x in self._destinations[route]]) + "\n"
        return res

class ADJ_RIB_in(BaseRib):

    def __init__(self, node_id, implicit_withdraw):
        BaseRib.__init__(self)
        self.node_id = node_id
        self.oktype = Route
        self._implicit_withdraw = implicit_withdraw

    def check(self, value):
        """check.

        :param value: check the type of value
        """
        if not isinstance(value, self.oktype):
            raise TypeError(value)

    def __loop_detection(self, route):
        if self.node_id in route.path:
            return True
        return False

    def filter(self, route):
        """filter.
        filter function for routes before the introduction in the rib
        returns always true for now

        :param route: route that needs to be evaluated
        :return: True
        """
        if self.__loop_detection(route):
            return True
        return False

    def insert(self, v):
        self.check(v)
        # input filter
        if self.filter(v):
            return None, None
        # check implicit withdraw
        substitute = None
        if self._implicit_withdraw:
            i = hash(v.addr)
            if i in self._destinations:
                for net in self._destinations[i]:
                    if net.nh == v.nh:
                        print("{}: Removing {} from rib".format(self.node_id, net))
                        substitute = net
                        self.remove(net)
        return super().insert(v), substitute

    def preference_ordering(self):
        for i in self._destinations:
            self._destinations[i] = sorted(self._destinations[i])

    def __str__(self):
        return "ADJ_RIB_in:\n" + super().__str__()

class LOC_rib(BaseRib):

    def __init__(self, node_id):
        BaseRib.__init__(self)
        self.node_id = node_id

    def __getitem__(self, i):
        """__getitem__.

        :param i: key addr
        :return: route object of the first element in the list of routes that
        are contained in the table at the i key
        """
        i = hash(i.addr)
        if i in self._destinations:
            return self._destinations[i][0]
        else:
            raise KeyError("{} key not found in the RIB".format(i))

    def insert(self, v):
        i = hash(v.addr)
        if i in self._destinations:
            if v == self._destinations[i][0]:
                return None
            del self._destinations[i]
        return super().insert(v)

    def __str__(self):
        return "LOC_rib:\n" + super().__str__()

class ADJ_RIB_out(BaseRib):

    def __init__(self, node_id):
        BaseRib.__init__(self)
        self.node_id = node_id
        self.withdraw_list = []
    
    def out_filters(self, route):
        return False

    def insert(self, v):
        if self.out_filters(v):
            return None
        if v in self.withdraw_list:
            self.remove_from_withdraws(v)
        return super().insert(v)
    
    def insert_withdraw(self, v):
        self.withdraw_list.append(v)

    def get_withdraws(self):
        return self.withdraw_list

    def remove_from_withdraws(self, route):
        self.withdraw_list.remove(route)

    def __str__(self):
        return "ADJ_RIB_out:\n" + super().__str__()

class BGP_RIB_handler():

    __ROUTE_COUNTER = 0

    def __init__(self, node_id, logger, implicit_withdraw: bool = True):
        self.node_id = node_id
        self.logger = logger
        self.adj_rib_in = ADJ_RIB_in(self.node_id, implicit_withdraw)
        self.loc_rib = LOC_rib(self.node_id)
        self.nodes_rib_out = {}
        self.rib_knowledge = {}
        self.local_state = set()

    def clean(self, implicit_withdraw):
        self.adj_rib_in = ADJ_RIB_in(self.node_id, implicit_withdraw)
        self.loc_rib = LOC_rib(self.node_id)
        for node in self.nodes_rib_out.keys():
            self.nodes_rib_out[node] = ADJ_RIB_out(node)
        self.rib_knowledge = {}
        self.local_state = set()
        BGP_RIB_handler.__ROUTE_COUNTER = 0

    def add_neighbor(self, neigh_id: str) -> None:
        if neigh_id in self.nodes_rib_out.keys():
            raise KeyError("{} neighbor is already present".format(neigh_id))
        self.nodes_rib_out[neigh_id] = ADJ_RIB_out(self.node_id)

    def rib_event_register(self, event):
        if event is not None:
            rib_change_event = Event(0, event.id, Events.RIB_CHANGE,
                                     None, None, obj=self.local_state)
        else:
            rib_change_event = Event(0, None, Events.RIB_CHANGE,
                                     None, None, obj=self.local_state)
        self.logger.log_rib_change(self.node_id, rib_change_event)

    def receive_withdraw(self, w_route, event: Event = None):
        try:
            for route in self.adj_rib_in[w_route]:
                if route == w_route:
                    if self.adj_rib_in.remove(route) == None:
                        self.local_state.remove(self.rib_knowledge[hash(w_route)])
                        self.rib_event_register(event)
                    if len(self.adj_rib_in[route]) == 0:
                        del self.adj_rib_in[route]
        except KeyError:
            print("{} - Error, I received a withdraw of a route that I don't \
                  know, ignored".format(self.node_id))

    def __add_to_knowledge(self, route: Route) -> None:
        if hash(route) not in self.rib_knowledge:
            self.rib_knowledge[hash(route)] = BGP_RIB_handler.__ROUTE_COUNTER
            BGP_RIB_handler.__ROUTE_COUNTER += 1

    def receive_advertisement(self, a_route: Route, event: Event = None) -> None:
        self.__add_to_knowledge(a_route)
        route, substitute = self.adj_rib_in.insert(a_route)
        if route is not None:
            if substitute != None:
                self.local_state.remove(self.rib_knowledge[hash(substitute)])
            self.local_state.add(self.rib_knowledge[hash(a_route)])
            self.rib_event_register(event)
        # TODO check if the events.RIB change is necessary

    def decision_process(self):
        # order routes by preference
        self.adj_rib_in.preference_ordering()
        # for each route insert the best in the loc_rib
        for destination in self.adj_rib_in:
            best_route = destination[0]
            print(best_route)
            print(self.loc_rib)
            # if there as been a change insert the new route in the adj-rib-out
            if self.loc_rib.insert(best_route) != None:
                for neigh in self.nodes_rib_out:
                    self.nodes_rib_out[neigh].insert(best_route)
            else:
                print("{} - destination already in the loc rib {}".format(self.node_id, best_route))
        for destination in self.loc_rib:
            if not self.adj_rib_in.exists(destination):
                del self.loc_rib[destination]
                for neigh in self.nodes_rib_out:
                    self.nodes_rib_out[neigh].insert_withdraw(destination)

    def exists(self, node_id):
        return node_id in self.nodes_rib_out.keys()

    def get_rib_out(self, node_id):
        if node_id not in self.nodes_rib_out.keys():
            raise KeyError("{} not in the nodes rib out dict".format(node_id))
        return self.nodes_rib_out[node_id]

    def __str__(self):
        res = "BGP RIB handler: \n"
        res += str(self.adj_rib_in)
        res += str(self.loc_rib)
        for node in self.nodes_rib_out.keys():
            res += str(node) + " " + str(self.nodes_rib_out[node])
        for route in self.rib_knowledge.keys():
            res += str(route) + " " + str(self.rib_knowledge[route]) + "\n"
        return res
