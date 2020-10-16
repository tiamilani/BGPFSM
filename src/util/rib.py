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
import ipaddress
from typing import Tuple, Any

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

class BaseRib(collections.MutableSequence): # pylint: disable=too-many-ancestors
    """BaseRib.
    Rib class used to manage rib information
    This is the general class that should be used to handle genral information
    All the Route information are contained in a destination dictionary.
    The route address is hashed and used as dictionary key.
    The object registered by the dictionary is a list of Route objects
    because for the same destination we can have multiple routes
    """

    insertion_response = Tuple[Route, None]
    key_type = Tuple[hash, None]

    def __init__(self):
        """__init__.
        """

        self._destinations = {}

    def __len__(self) -> int:
        """__len__.
        Get the number of destinations registered by the RIB

        :rtype: int
        """
        return len(self._destinations)

    def __getitem__(self, i: Route) -> list:
        """__getitem__.
        Return a list of routes associated with a destination

        :param i: Route used to search, only the addr will be used
        :type i: route
        :rtype: list

        :raise: KeyError if the destination address is not in the dictionary
        """
        i = hash(i.addr)
        if i in self._destinations:
            return self._destinations[i]
        raise KeyError("{} key not found in the RIB".format(i))

    def __delitem__(self, i: Route) -> None:
        """__delitem__.
        Remove one destination list, it will remove all the routes
        associated with the destiantion and the destination itself from
        the destinations dictionary

        :param i: Route used for the lookup
        :type i: Route
        :rtype: None

        :raise: KeyError if the destination address is not in the dictionary
        """
        i = hash(i.addr)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        del self._destinations[i]

    def __setitem__(self, i: Route, v: list) -> None:
        """__setitem__.
        Change one rib entrance with another list of routes


        :param i: Lookup route
        :type i: Route
        :param v: List of routes to substitute
        :type v: list
        :rtype: None

        :raise: KeyError if the destination address is not in the dictionary
        """
        i = hash(i.addr)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        self._destinations[i] = v

    def contains(self, i: ipaddress.IPv4Network, value: Route) -> bool:
        """contains.
        Check if the rib contains a specific route inside the desintations

        :param i: Lookup address for the destinations dictionary
        :type i: ipaddress.IPv4Network
        :param value: Value to check
        :type value: Route
        :rtype: bool

        :raise: KeyError if the destination address is not in the dictionary
        """
        i = hash(i)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        if value in self._destinations[i]:
            return True
        return False

    def remove(self, v: Route) -> insertion_response: # pylint: disable=arguments-differ, undefined-variable
        """remove.
        Remove a single route from the dictionary

        :param v: Route to remove
        :type v: Route
        :rtype: insertion_response, None if the route has been removed, the route
        itself otherwise

        :raise: KeyError if the destination address is not in the dictionary
        """
        i = hash(v.addr)
        if i not in self._destinations:
            raise KeyError("{} key not found in the RIB".format(i))
        if v in self._destinations[i]:
            self._destinations[i].remove(v)
            return None
        return v

    def insert(self, v: Route) -> insertion_response: # pylint: disable=arguments-differ, undefined-variable
        """insert.
        Insert a route in the RIB

        :param v: Route to insert
        :type v: Route
        :rtype: insertion_response non if there route has not been inserted
        the route itself otherwise
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

    def keys(self) -> list:
        """keys.

        :rtype: list
        """
        return self._destinations.keys()

    def exists(self, destination: Route) -> bool:
        """exists.
        check if a destiantion exists in the dictionary keys, the address of
        the route will be used for generic lookup

        :param destination: Lookup destination
        :type destination: Route
        :rtype: bool
        """
        i = hash(destination.addr)
        return i in self.keys()

    def get_key(self, i) -> key_type: # pylint: disable=undefined-variable
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

    def __str__(self) -> str:
        """__str__.
        Returns the RIB in a human readable format

        :rtype: str
        """
        dest_table = sorted(self._destinations)
        res = ""
        for route in dest_table:
            res += str([str(x) for x in self._destinations[route]]) + "\n"
        return res

class ADJ_RIB_in(BaseRib): # pylint: disable=invalid-name, too-many-ancestors
    """ADJ_RIB_in.
    Class used to manage ADJ-RIB-in objects
    Follow the explanations in the RFC 4271 to see the differences between the
    other RIB inside a BGP speaker.
    The main purpose of this rib is to manage the incoming information from
    the otuside, keep multiple routes for the same destination and substitute
    paths when needed.
    It contains also the function to order all the routes by preference.
    """

    ADJ_RIB_in_response = Tuple[BaseRib.insertion_response, Route]

    def __init__(self, node_id: str, implicit_withdraw: bool):
        """__init__.

        :param node_id: Id of the node that controls this ADJ-RIB-in
        :type node_id: str
        :param implicit_withdraw: Implicit withdraw parameter, used to delete
        routes without an explicit withdraw but with a variation in the best
        route of the next path
        :type implicit_withdraw: bool
        """
        BaseRib.__init__(self)
        self.node_id = node_id
        self.oktype = Route
        self._implicit_withdraw = implicit_withdraw

    def check(self, value: Any) -> None:
        """check.
        Check that a value is an instance of the type required, otherwise
        it will raise an exception

        :param value: Value to check
        :type value: Any
        :rtype: None

        :raise: TypeError if the value is not of type Route
        """
        if not isinstance(value, self.oktype):
            raise TypeError(value)

    def __loop_detection(self, route: Route) -> bool:
        """__loop_detection.
        Function to avoid loops in a received route
        Filter function

        :param route: Route to check
        :type route: Route
        :rtype: bool
        """
        if self.node_id in route.path:
            return True
        return False

    def filter(self, route: Route) -> bool:
        """filter.
        Filters that needs to be applyied to the Route before the introduction
        in the rib.
        A route must pass all the checks

        :param route: Route that needs to be checked
        :type route: Route
        :rtype: bool
        """
        if self.__loop_detection(route):
            return True
        return False

    def insert(self, v: Route) -> ADJ_RIB_in_response: # pylint: disable=undefined-variable
        """insert.
        Function to introduce a new Route in the ADJ-RIB-in
        A route must be an instance of the Route class
        A route must pass all the input filters
        If the implicit withdraw is active and the Route has passed all the
        previous tests then will be checked if the next hope has already
        shared a best path. If a best path to the destination from the route NH
        already exists it will be deleted and the new best path will be inserted.
        This operation will also return the subsituted route.
        If the implicit withdraw option is not active the the route will be added
        without any other checks.
        If the route has not passed the filters but Implicit withdraw is active
        the route will not be added to the RIB, but the previous best path from
        the NH (if exists) will be deleted anyway.

        :param v: Route to add
        :type v: Route
        :rtype: ADJ_RIB_in_response tuple containing in the first place the result
        of the insert, None if the route has not been added, The route itself
        if it has been added. The second component of the Tuple is the route
        that has been substituted by the one inserted.
        """
        self.check(v)
        # input filter
        filtered = False
        if self.filter(v):
            filtered = True
        # check implicit withdraw
        substitute = None
        if self._implicit_withdraw:
            i = hash(v.addr)
            if i in self._destinations:
                for net in self._destinations[i]:
                    if net.nh == v.nh:
                        substitute = net
                        self.remove(net)
        if not filtered:
            return super().insert(v), substitute
        return None, substitute

    def preference_ordering(self) -> None:
        """preference_ordering.
        Order all the destinations lists by the preference order
        This function implies that the Route object has order functions.

        :rtype: None
        """
        for i in self._destinations:
            self._destinations[i] = sorted(self._destinations[i])

    def __str__(self) -> str:
        """__str__.
        Return the ADJ_RIB_in in a human readable format

        :rtype: str
        """
        return "ADJ_RIB_in:\n" + super().__str__()

class LOC_rib(BaseRib): # pylint: disable=invalid-name, too-many-ancestors
    """LOC_rib.
    Class used to controll the LOC_rib implementation.
    For more specific information about this resource use the RFC 4271
    The goal of this RIB is to contains only the best paths to the destiantions.
    Those will be also the paths installed by the node in the Routing table
    """


    def __init__(self, node_id: str):
        """__init__.

        :param node_id: Id of the node that controls this LOC rib
        :type node_id: str
        """
        BaseRib.__init__(self)
        self.node_id = node_id

    def __getitem__(self, i: Route) -> Route:
        """__getitem__.
        Returns the first item in the list of objects of this RIB.

        :param i: Route which ipaddress will be used for the lookup
        :type i: Route
        :rtype: Route
        :raise: KeyError
        """
        i = hash(i.addr)
        if i in self._destinations:
            return self._destinations[i][0]
        raise KeyError("{} key not found in the RIB".format(i))

    def insert(self, v: Route) -> BaseRib.insertion_response:
        """insert.
        Insertion function for the LOC-rib
        This insertion function will delete the previous item that was
        previously saved at that address in the rib.
        The the passed route will be inserted.
        If the Route has already been in the loc rib it wont be inserted
        and the function will return None

        :param v: Route to introduce
        :type v: Route
        :rtype: BaseRib.insertion_response See the rib insertion function
        to see the possible value
        """
        i = hash(v.addr)
        if i in self._destinations:
            if v == self._destinations[i][0]:
                return None
            del self._destinations[i]
        return super().insert(v)

    def __str__(self) -> str:
        """__str__.
        Returns the LOC_rib in a human readable format

        :rtype: str
        """
        return "LOC_rib:\n" + super().__str__()

class ADJ_RIB_out(BaseRib): # pylint: disable=invalid-name, too-many-ancestors
    """ADJ_RIB_out.
    Class used to controll an ADJ_RIB_out object
    This object is similar to the ADJ_RIB_in but it's the opposit case.
    In this rib we want to keep the routes that will be shared to a neighbour.
    The out rib is personal for each neighbour.
    """


    def __init__(self, node_id: str):
        """__init__.

        :param node_id: Id of the node that controls this ADJ_RIB_out
        :type node_id: str
        """
        BaseRib.__init__(self)
        self.node_id = node_id
        self.withdraws = {}

    def out_filters(self, route: Route) -> bool: # pylint: disable=unused-argument, no-self-use
        """out_filters.
        Filters that needs to be applyied before sending out a route
        For now there are no out filters so the route will always pass this check

        :param route: Route
        :type route: Route
        :rtype: bool Always False
        """
        return False

    def insert(self, v: Route) -> BaseRib.insertion_response:
        """insert.
        Insert function in the ADJ_RIB_out.
        To be inserted in the ADJ_RIB_out a route must not be filtered out
        If the route was in the withdraw list the will be removed from that
        list and added to the destination list for the sharing as an
        advertisement.
        If the network was in the withdraw list then my neighbour already
        knows of this network so I should not send an advertisement of
        it but just leave the queue as it is

        :param v: Route to share
        :type v: Route
        :rtype: BaseRib.insertion_response
        """
        if self.out_filters(v):
            return None
        i = hash(v.addr)
        if i in self.withdraws.keys() and v in self.withdraws[i]:
            self.remove_from_withdraws(v)
            return None
        if i in self._destinations:
            if v in self._destinations[i]:
                return None
            del self._destinations[i]
        return super().insert(v)

    def insert_withdraw(self, route: Route) -> None:
        """insert_withdraw.
        Function to introduce a new withdraw of a network
        If the network was in the destiantions list for the advertisement then
        it will be removed and nothing will be sent to the neighbour.

        :param route: Route to insert in the withdraw list
        :type route: Route
        :rtype: None
        """
        if super().exists(route) and super().contains(route.addr, route):
            super().remove(route)
            if len(self._destinations[hash(route.addr)]) == 0:
                del self._destinations[hash(route.addr)]
            return
        i = hash(route.addr)
        if i not in self.withdraws.keys():
            self.withdraws[i] = [route]
        elif route not in self.withdraws[i]:
            self.withdraws[i].append(route)

    def exists_withdraws(self, route: Route) -> bool:
        """exists_withdraws.
        Check if an addr is already present in the withdraw list

        :param route: Route used as lookup for the address
        :type route: Route
        :rtype: bool
        """
        return hash(route.addr) in self.withdraws.keys()

    def get_withdraws_keys(self) -> list:
        """get_withdraws_keys.
        Return the keys in the withdraw dictionary as a list

        :rtype: list
        """
        return list(self.withdraws.keys())

    def get_withdraws(self, index: Tuple[int, Route]) -> list:
        """get_withdraws.
        Get the withdraws for a single address, you can used as lookup system
        a route, which the address will be used or directly an hash as integer

        :param index: Index to lookup for
        :type index: Tuple[int, Route]
        :rtype: list
        """
        if isinstance(index, Route):
            index = hash(index.addr)
        return self.withdraws[index]

    def remove_from_withdraws(self, route: Route) -> None:
        """remove_from_withdraws.
        Remove a route from the withdraws system

        :param route: Route to remove
        :type route: Route
        :rtype: None

        :raise: KeyError if the key is not present in the dictionary
        """
        if hash(route.addr) not in self.withdraws.keys():
            raise KeyError("{} not in the withdraws".format(route.addr))
        self.withdraws[hash(route.addr)].remove(route)

    def del_withdraws(self, index: hash) -> None:
        """del_withdraws.
        Remove a withdraw address from the dictionary
        Will be also removed all the routes inside the dictionary element

        :param index: Lookup hash address
        :type index: hash
        :rtype: None
        """
        del self.withdraws[index]

    def __str__(self) -> str:
        """__str__.
        Translate in a human readable format the ADJ-RIB-out

        :rtype: str
        """
        return "ADJ_RIB_out:\n" + super().__str__() + "\nWithdraw List: " \
               + str([str(self.withdraws[x]) for x in self.withdraws]) + "\n"

class BGP_RIB_handler(): # pylint: disable=invalid-name
    """BGP_RIB_handler.
    Generic BGP rib handler
    This object can manage all the RIBs of a BGP node.
    ADJ-RIB-in, ADJ-RIB-out, LOC-RIB
    It will use the classes defined for each one of those purposes
    Is possible to insert advertisement or withdraws, call the decision process
    and retrieve for each neighbour it's own ADJ-RIB-out
    """


    __ROUTE_COUNTER = 0

    def __init__(self, node_id, logger, implicit_withdraw: bool = True):
        """__init__.

        :param node_id: id of the node that controls this object
        :param logger: Logger of the node
        :param implicit_withdraw: Boolean value that describes if the
        implicit withdraw option is active, (default = True)
        :type implicit_withdraw: bool
        """
        self.node_id = node_id
        self.logger = logger
        self.adj_rib_in = ADJ_RIB_in(self.node_id, implicit_withdraw)
        self.loc_rib = LOC_rib(self.node_id)
        self.nodes_rib_out = {}
        self.rib_knowledge = {}
        self.local_state = set()

    def add_neighbor(self, neigh_id: str) -> None:
        """add_neighbor.
        Function used to insert a new neighbour in the set
        This function will create a new ADJ-RIB-out object for the neighbour

        :param neigh_id: id of the neighbour node
        :type neigh_id: str
        :rtype: None
        """
        if neigh_id in self.nodes_rib_out.keys():
            raise KeyError("{} neighbor is already present".format(neigh_id))
        self.nodes_rib_out[neigh_id] = ADJ_RIB_out(self.node_id)

    def rib_event_register(self, event: Event) -> None:
        """rib_event_register.
        Function used to register a RIB change event
        In the logger will be registered the change in the RIB

        :param event: Event that triggers the rib change event
        :type event: Event
        :rtype: None
        """
        if event is not None:
            rib_change_event = Event(0, event.id, Events.RIB_CHANGE,
                                     None, None, obj=self.local_state)
        else:
            rib_change_event = Event(0, None, Events.RIB_CHANGE,
                                     None, None, obj=self.local_state)
        self.logger.log_rib_change(self.node_id, rib_change_event)

    def receive_withdraw(self, w_route: Route, event: Event = None) -> None:
        """receive_withdraw.
        Function used to register a withdraw of a route from a neighbour
        The route will be evaluated, if the rote is in the ADJ-RIB-in
        it will be removed and the state will be updated.

        :param w_route: Route to withdraw
        :type w_route: Route
        :param event: Reception event that triggered the deletion
        :type event: Event
        :rtype: None
        """
        try:
            for route in self.adj_rib_in[w_route]:
                if route == w_route:
                    if self.adj_rib_in.remove(route) is None:
                        self.local_state.remove(self.rib_knowledge[hash(w_route)])
                        self.rib_event_register(event)
                    if len(self.adj_rib_in[route]) == 0:
                        del self.adj_rib_in[route]
        except KeyError:
            print("{} - Error, I received a withdraw of a route that I don't \
                  know, ignored".format(self.node_id))
            return

    def __add_to_knowledge(self, route: Route) -> None:
        """__add_to_knowledge.
        Add a new route to the general knowledge of the node with a specific ID
        If the route is already present will be ignored

        :param route: Route to add to the knowledge
        :type route: Route
        :rtype: None
        """
        if hash(route) not in self.rib_knowledge:
            self.rib_knowledge[hash(route)] = BGP_RIB_handler.__ROUTE_COUNTER
            BGP_RIB_handler.__ROUTE_COUNTER += 1

    def receive_advertisement(self, a_route: Route, event: Event = None) -> None:
        """receive_advertisement.
        Function that handle a new advertisement of a route.
        The route will be inserted in the ADJ-RIB-in.
        If the result is positive the local state will be updated and the event
        will be registered.
        It is also possible to substitute the knowledge when the route substitute
        another route in the ADJ-RIB-in

        :param a_route: Route to insert
        :type a_route: Route
        :param event: RX event that triggers the inclusion of this route
        :type event: Event
        :rtype: None
        """
        # Add the route to the common knowledge
        self.__add_to_knowledge(a_route)
        # Register the route
        route, substitute = self.adj_rib_in.insert(a_route)
        # If the route has been registered then check for substitutes and
        # log the event
        if route is not None:
            if substitute is not None:
                self.local_state.remove(self.rib_knowledge[hash(substitute)])
            self.local_state.add(self.rib_knowledge[hash(a_route)])
            self.rib_event_register(event)
        if route is None and substitute is not None:
            if len(self.adj_rib_in[a_route]) == 0:
                del self.adj_rib_in[a_route]
            self.local_state.remove(self.rib_knowledge[hash(substitute)])

    def decision_process(self) -> None:
        """decision_process.
        Execute the decision process on the local ADJ-RIB-in.
        This process is decribed more deaply in RFC 4271.
        The ADJ-RIB-in will be ordered using the preference of each route for
        each destination.
        The for each destination in the ADJ-RIB-in will be take the first
        route (the prefered one by the node policies).
        If present, the old best route for the destiantion will be registered.
        If the route has been inserted correctly in the LOC-RIB then will
        be evaluated the introduction in the ADJ-RIB-out of each neighbour.
        If the ADJ_RIB_out doesn't contains anything for the destiantion
        then an advertisement will be added and a withdraw for the previous best
        if present.
        If there was something in the ADJ-RIB-out then it has to be updated.
        The advertisement will be substituted with the new best route to send
        if was not programmed a withdraw of the same route.
        In this last case nothing will be added and the withdraw will be removed.
        This is to avoid the case (W1, A1) in the same cicle.

        :rtype: None
        """
        # order routes by preference
        self.adj_rib_in.preference_ordering()
        # for each route insert the best in the loc_rib
        for destination in self.adj_rib_in:
            best_route = destination[0]
            # if there as been a change insert the new route in the adj-rib-out
            old_best = None
            if self.loc_rib.exists(best_route):
                old_best = self.loc_rib[best_route]
            if self.loc_rib.insert(best_route) is not None:
                for neigh in self.nodes_rib_out:
                    # Case 1, the RIB out doesn't contains a route for the destination
                    if not self.nodes_rib_out[neigh].exists(best_route):
                        # Insert the new best as an Advertisement
                        self.nodes_rib_out[neigh].insert(best_route)
                        # If the Old best is not none insert it as a withdraw
                        if old_best is not None and \
                           not self.nodes_rib_out[neigh].exists_withdraws(best_route):
                            self.nodes_rib_out[neigh].insert_withdraw(old_best)
                    # Case 2, The Rib contains a Route for the detination
                    else:
                        # Remove the route from the advertisements
                        self.nodes_rib_out[neigh].remove(old_best)
                        if len(self.nodes_rib_out[neigh][old_best]) == 0:
                            del self.nodes_rib_out[neigh][old_best]
                        # If the route in the withdraws is equal to the new best don't do anything
                        # Otherwise insert the new route as an advertisement
                        if self.nodes_rib_out[neigh].exists_withdraws(best_route) and \
                           best_route in self.nodes_rib_out[neigh].get_withdraws(best_route):
                            self.nodes_rib_out[neigh].remove_from_withdraws(best_route)
                        else:
                            self.nodes_rib_out[neigh].insert(best_route)
        # Evaluation if something has to be removed from the LOC rib and withdrawd
        for destination in self.loc_rib:
            if not self.adj_rib_in.exists(destination):
                del self.loc_rib[destination]
                for neigh in self.nodes_rib_out:
                    # if self.nodes_rib_out[neigh].exists(destination):
                    #    del self.nodes_rib_out[neigh][destination]
                    self.nodes_rib_out[neigh].insert_withdraw(destination)

    def exists(self, node_id: str) -> bool:
        """exists.
        Check if a node ADJ-RIB-out exists

        :param node_id: Node id to check for
        :type node_id: str
        :rtype: bool
        """
        return node_id in self.nodes_rib_out.keys()

    def get_rib_out(self, node_id: str) -> ADJ_RIB_out:
        """get_rib_out.
        Get the rib out of a node

        :param node_id: node to look for
        :type node_id: str
        :rtype: ADJ_RIB_out
        :raise: KeyError in case the neighbour was unknown
        """
        if node_id not in self.nodes_rib_out.keys():
            raise KeyError("{} not in the nodes rib out dict".format(node_id))
        return self.nodes_rib_out[node_id]

    def __str__(self) -> str:
        """__str__.
        Get all the RIBs in a human readable format

        :rtype: str
        """
        res = "BGP RIB handler: \n"
        res += str(self.adj_rib_in)
        res += str(self.loc_rib)
        for node in self.nodes_rib_out:
            res += str(node) + " " + str(self.nodes_rib_out[node])
        return res
