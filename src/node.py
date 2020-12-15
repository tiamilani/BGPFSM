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
node module
===========

Module used to represent a node in the network.
All the node logic is inside this module

"""

# pylint: disable=cyclic-import

import sys
import ipaddress
import math
from copy import deepcopy
import simpy

sys.path.insert(1, 'util')
from module import Module
from event import Event
from events import Events
from packet import Packet
from link import Link
from routingTable import RoutingTable
from route import Route
from distribution import Distribution
from rib import BGP_RIB_handler
from policies import PolicyValue

import bgp_sim

class Node(Module):
    """Node.
    Class to manage node inside the simulation
    """

    # States of the node
    IDLE = 0
    STATE_CHANGING = 1

    # Param that the node can get from the configuration
    # Distribution for the message transmission
    PAR_DATARATE = "datarate"
    # Processing time distribution
    PAR_PROC_TIME = "processing"
    # Message arrival time distribution
    PAR_DELAY = "delay"
    # Withdraw param
    PAR_WITHDRAW = "withdraw"
    # Withdraw distribution
    PAR_WITHDRAW_DIST = "withdraw_dist"
    # reannouncement param
    PAR_REANNOUNCE = "reannouncement"
    # Reannouncement distribution
    PAR_REANNOUNCE_DIST = "reannouncement_dist"
    # Signaling param
    PAR_SIGNALING = "signaling"
    # Signaling sequence
    PAR_SIGNALING_SEQUENCE = "signaling_sequence"
    # Implicit withdraw flag
    PAR_IMPLICIT_WITHDRAW = "implicit_withdraw"

    def __init__(self, id_node, config):
        """__init__.

        :param id_node: identifier of the node
        :param config: Configuration file
        """
        self._id = id_node
        # Initial state of the node is IDLE
        self._state = Node.IDLE
        # Simulation environment
        self._env = bgp_sim.Sim.Instance().env # pylint: disable=no-member
        # Initialization of commond modules
        Module.__init__(self)
        # Events queue, events that needs to be handle by the node
        self.event_store = simpy.Store(self._env)
        # Routing table, This table represent the routing knowledge
        # actually present in the node
        self.routing_table = RoutingTable()
        # Implicit withdraw flag
        self.implicit_withdraw = config.get_param(Node.PAR_IMPLICIT_WITHDRAW) in ("True", "true")
        # Rib table, this table represent all the routing knowledge
        # present in the node, plus routes that are not the best
        self.rib_handler = BGP_RIB_handler(self._id, self.logger, self.implicit_withdraw)
        # Event handler of a node
        self.reception = self._env.process(self.handle_event())
        # Neighbor of the node
        self._neighbors = {}
        # Destinations of the node
        self._destinations = []
        # Withdraw flag
        self.withdraw = config.get_param(Node.PAR_WITHDRAW) in ("True", "true")
        # Reannouncement flag
        self.reannounce = config.get_param(Node.PAR_REANNOUNCE) in ("True", "true")
        # Signaling flag
        self.signaling = config.get_param(Node.PAR_SIGNALING) in ("True", "true")
        # Distributions used inside the node
        self.rate = Distribution(config.get_param(Node.PAR_DATARATE))
        self.proc_time = Distribution(config.get_param(Node.PAR_PROC_TIME))
        self.delay = Distribution(config.get_param(Node.PAR_DELAY))
        self.withdraw_dist = Distribution(config.get_param(Node.PAR_WITHDRAW_DIST))
        self.reannouncement_dist= Distribution(config.get_param(Node.PAR_REANNOUNCE_DIST))
        # Signaling sequence
        self.signaling_sequence = list(config.get_param(Node.PAR_SIGNALING_SEQUENCE))
        self.signaling_accepted_simbols = ["A", "W"]
        # Resource for the acquisition of the tx channel resource
        self.processing_res = simpy.Resource(self._env, capacity=1)
        self.__already_scheduled_decision_process = False
        # MRAI for withdraws flag
        self.mrai_withdraw = False
        self.rfd = None
        self.adaptive_rfd = False

    def _print(self, msg: str) -> None:
        """_print.
        Print a message from the node
        evaluate the verbose level before printing a message

        :param msg: Message that needs to be printed on sysout
        :type msg: str
        :rtype: None
        """
        if self.verbose:
            print("{}-{} ".format(self._env.now, self._id) + msg)

    def add_neighbor(self, link: Link) -> None:
        """
        Add a neighbor to the set of neighbors
        If the neighbor is already in the set it throws an error
        and terminate

        :param link: link that has to be added
        :type link: Link
        :rtype: None
        """
        # Evaluate if the link is already present
        if link.id not in self._neighbors:
            self._neighbors[link.node.id] = link
            # Add the neighbour to the list in the rib
            self.rib_handler.add_neighbor(link.node.id)

        else:
            self._print("{} - Neighbor {} already in the set".format(self._id,
                                                                link.node.id))
            sys.exit(1)

    def evaluate_signaling_event(self, elem: str) -> Event:
        """evaluate_signaling_event.

        Evaluate a signaling event and returns the event associated with the
        sigaling

        :param elem: signal to manage
        :type elem: str
        :rtype: Event

        :raise ValueError: When is passed an element that is not a valid signal
        """
        # Evaluate if the element is an advertisement
        if elem == "A":
            proc_time = self.reannouncement_dist.get_value()
            event = Event(proc_time, None, Events.INTRODUCE_NETWORKS, self, self,
                          obj=None)
        # Evaluate if the element is a withdraw
        elif elem == "W":
            withdraw_time = self.withdraw_dist.get_value()
            event = Event(withdraw_time, None, Events.REMOVE_NETWORKS, self, self,
                          obj=None)
        else:
            raise ValueError("Elem {} not accepted in signaling, accepted \
                              simbols: {}".format(elem,
                                self.signaling_accepted_simbols))
        return event


    def force_share_dst(self):
        """force_share_dst.
        Function used as kick starter for nodes that have to share a destination
        to generate the start events.
        """
        if len(self._destinations) > 0:
            if not self.signaling:
                proc_time = self.proc_time.get_value()
                decision_process = Event(proc_time, None, Events.INTRODUCE_NETWORKS,
                                      self, self, obj=None)
                self.event_store.put(decision_process)
            else:
                env_time = 0
                for elem in self.signaling_sequence:
                    event = self.evaluate_signaling_event(elem)
                    self._print("New event to signal: {}, delay: {}".format(
                                env_time, event.event_duration))
                    env_time += event.event_duration
                    event.event_duration = env_time
                    self.event_store.put(event)

    def __remove_from_history(self, history_obj: Route) -> None:
        """
        __remove_from_history
        Function to remove a route from the history, it will also take care
        of deleting possible events of the route.

        :param history_obj: Route to remove
        :type history_obj: Route
        """
        self.rib_handler.history_rib.remove(history_obj)
        if history_obj.reusable_event is not None:
            history_obj.reusable_event.interrupt()
            history_obj.reusable_event = None
        if history_obj.t_hold_event is not None:
            history_obj.t_hold_event.interrupt()
            history_obj.t_hold_event = None

    def __update_figure_of_merit_filter(self, route: Route, t_diff: float, rfd_filter) -> None:
        # The route was already reachable so I have to use the
        # decay function appropriated
        delta_t = rfd_filter.delta_t
        index = math.floor(t_diff / delta_t)
        if index >= rfd_filter.decay_array_size:
            route.figure_of_merit = 0
            route.flaps = 0
            # I don't have any more memory of flaps of this route
            # so I can remove it from the history
            self.rib_handler.history_rib.remove(route)
        else:
            route.figure_of_merit = route.figure_of_merit * rfd_filter.decay_mult(index)

    def __update_figure_of_merit(self, history_route: Route, t_diff: int) -> None:
        if history_route.reachable:
            self.__update_figure_of_merit_filter(history_route, t_diff, self.rfd.rfd_ok)
        else:
            # The route was not reachable so I have to use the other
            # figure of merit decay function
            self.__update_figure_of_merit_filter(history_route, t_diff, self.rfd.rfd_ng)

    def __increase_figure_of_merit(self, history_route: Route, route: Route, value: float,
                                   ceiling: float) -> None:
        if not self.adaptive_rfd or len(route.path) == 0:
            history_route.figure_of_merit += value
        else:
            history_route.figure_of_merit += value * 1/len(route.path)
        if history_route.figure_of_merit > ceiling:
            history_route.figure_of_merit = ceiling

    def __copy_history_values(self, route: Route, history_route: Route, reachable: bool) -> None:
        route.figure_of_merit = history_route.figure_of_merit 
        route.last_time_updated = self._env.now
        route.usable = history_route.usable
        route.reachable = reachable
        route.reusable_event = history_route.reusable_event
        route.flaps = history_route.flaps
        route.first_suppressed_time = history_route.first_suppressed_time
        route.t_hold_event = history_route.t_hold_event

    def __calculate_decay_time(self, route, rfd_filter) -> float:
        decay_minutes = rfd_filter.decay / 60
        t = math.log2((self.rfd.reuse/route.figure_of_merit) ** -decay_minutes)
        t = t * 60
        index = math.ceil(t/rfd_filter.delta_t)

        if index >= rfd_filter.decay_array_size:
            t = rfd_filter.decay_memory_limit + rfd_filter.delta_t

        return t

    def new_network(self, route: Route, event: Event) -> None:
        """new_network.
        Function used to add a new route, it will be evaluated for the
        insertion in the rib and it will be then evaluated for the Routing table

        :param route: Route to evaluate
        :type route: Route
        :param event: Cause event for the evaluation
        :type event: Event
        :rtype: None
        """
        if self.rfd is not None:
            #RFD evaluation of an announcement

            # Check if I lost memory of that route in the history_rib
            if self.rib_handler.history_rib.exists(route):
                # The route exists in the history, I have to check since when is in the history
                history_route = self.rib_handler.history_rib[route]
                t_diff = self._env.now - history_route.last_time_updated
                # Check both decading rates
                if history_route.reachable:
                    delta_t = self.rfd.rfd_ok.delta_t
                    index = math.floor(t_diff / delta_t)
                    # If the index is larger than the max size of the vector I can remove
                    # the route from the history because I don't have any memory
                    # of it's flaps
                    if index >= self.rfd.rfd_ok.decay_array_size:
                        self._print("{} removed from the history because stable enough")
                        self.__remove_from_history(history_route)
                else:
                    delta_t = self.rfd.rfd_ng.delta_t
                    index = math.floor(t_diff / delta_t)
                    if index >= self.rfd.rfd_ng.decay_array_size:
                        self._print("{} removed from the history because stable enough")
                        self.__remove_from_history(history_route)

            # Check if the route is a change from a known neighbour, 
            # so I have to treate it as an implicit withdraw
            if self.rib_handler.adj_rib_in.exists(route):
                for net in self.rib_handler.adj_rib_in[route]:
                    if net.nh == route.nh:
                        self._print("This neighbor has changed best path")
                        self.rib_handler.history_rib.insert(net)
            # If I don't have flaps history about this route I can use it without
            # problems
            if route.mine or not self.rib_handler.history_rib.exists(route):
                route.usable = True
                route.figure_of_merit = 0
                event.obj = (str(route), route.figure_of_merit)
                self.logger.log_figure_of_merit(self, event)
                route.flaps = 0
                route.last_time_updated = self._env.now
                self.rib_handler.receive_advertisement(route, event)
            else:
                # if history_route and route are not equal then treat the new 
                # route arrived as a withdraw but with the correct penalty
                # if history_route and the route are equal then treat it as a
                # reannouncement
                history_route = self.rib_handler.history_rib[route]
                t_diff = self._env.now - history_route.last_time_updated
                self.__update_figure_of_merit(history_route, t_diff)

                # Log the actual figure of merit
                event.obj = (str(history_route), history_route.figure_of_merit)
                self.logger.log_figure_of_merit(self, event)
                # Add the reannouncement penalty
                if history_route.path != route.path:
                    self._print("It's an attribute change")
                    self.__increase_figure_of_merit(history_route, route, self.rfd.ac_penalty,
                                                    self.rfd.rfd_ok.ceiling)
                    history_route.flaps += 1
                    self.rib_handler.receive_withdraw(history_route, event)
                else:
                    self._print("It's a reannouncement")
                    self.__increase_figure_of_merit(history_route, route, self.rfd.ra_penalty,
                                                    self.rfd.rfd_ok.ceiling)
                    history_route.flaps += 1

                self._print("{} New figure of merit: {}, flapped: {}".format(route, 
                    history_route.figure_of_merit, history_route.flaps))
                event.obj = (str(history_route), history_route.figure_of_merit)
                self.logger.log_figure_of_merit(self, event)
    
                # Substitute the old route with the new one, with the updated
                # variables
                self.__copy_history_values(route, history_route, True)
                res = self.rib_handler.history_rib.insert(route)

                # Evaluate if it is possible to use the route
                if route.usable and route.figure_of_merit < self.rfd.cut:
                    self.rib_handler.receive_advertisement(route, event)
                elif not route.usable and route.figure_of_merit < self.rfd.reuse:
                    self._print("{} the route is now usable".format(route))
                    event.obj = route
                    self.logger.log_route_reusable(self, event)
                    route.usable = True
                    # Remove route from a reuse list
                    # not sure it's correct, it should be enough to set it as usable
                    # and leave it to finish it's merit
                    # self.rib_handler.history_rib.remove(route)
                    # Use the route
                    if route.reusable_event is not None:
                        route.reusable_event.interrupt()
                        route.reusable_event = None
                    if route.t_hold_event is not None:
                        route.t_hold_event.interrupt()
                        route.t_hold_event = None
                    self.rib_handler.receive_advertisement(route, event)
                else:
                    route.usable = False
                    if route.t_hold_event is None:
                        route.first_suppressed_time = self._env.now
                        self._print("{} SUPPRESSED".format(route))
                        event.obj = route
                        self.logger.log_route_suppressed(self, event)

                        t_hold_event = Event(self.rfd.t_hold, event.id, Events.END_T_HOLD,
                                              self, self, obj=route)
                        self.event_store.put(t_hold_event)

                    t = self.__calculate_decay_time(route, self.rfd.rfd_ok)
                    self._print("{} will be available again in {}s".format(route, t))

                    reuse_process = Event(t, event.id, Events.ROUTE_REUSABLE,
                                          self, self, obj=route)
                    self.event_store.put(reuse_process)
                    self.rib_handler.history_rib.insert(route)
                
                if route.figure_of_merit == 0:
                    route.flaps = 0
                    self.__remove_from_history(route)
        else:
            self.rib_handler.receive_advertisement(route, event)

    def remove_network(self, route: Route, event: Event) -> None:
        """remove_network.
        Function used to add a new route, it will be evaluated for the
        insertion in the rib and it will be then evaluated for the Routing table

        :param route: Route to evaluate
        :type route: Route
        :param event: Cause event for the evaluation
        :type event: Event
        :rtype: None
        """
        if self.rfd is not None:
            # RFD evaluation for the reception of a withdraw

            # If there is no history of flapping
            # Check if I lost memory of that route in the history_rib
            if self.rib_handler.history_rib.exists(route):
                # The route exists in the history, I have to check since when is in the history
                history_route = self.rib_handler.history_rib[route]
                t_diff = self._env.now - history_route.last_time_updated
                # Check both decading rates
                if history_route.reachable:
                    delta_t = self.rfd.rfd_ok.delta_t
                    index = math.floor(t_diff / delta_t)
                    # If the index is larger than the max size of the vector I can remove
                    # the route from the history because I don't have any memory
                    # of it's flaps
                    if index >= self.rfd.rfd_ok.decay_array_size:
                        self._print("{} removed from the history because stable enough")
                        self.__remove_from_history(history_route)
                else:
                    delta_t = self.rfd.rfd_ng.delta_t
                    index = math.floor(t_diff / delta_t)
                    if index >= self.rfd.rfd_ng.decay_array_size:
                        self._print("{} removed from the history because stable enough")
                        self.__remove_from_history(history_route)

            if route.mine or not self.rib_handler.history_rib.exists(route):
                route.figure_of_merit = 0
                self.__increase_figure_of_merit(route, route, self.rfd.w_penalty, 
                                                self.rfd.rfd_ng.ceiling)
                event.obj = (str(route), route.figure_of_merit)
                self.logger.log_figure_of_merit(self, event)
                route.last_time_updated = self._env.now
                route.flaps = 0
                route.usable = True
                route.reachable = False
                self.rib_handler.history_rib.insert(route)
                self.rib_handler.receive_withdraw(route, event)
            else:
                history_route = self.rib_handler.history_rib[route]
                t_diff = self._env.now - history_route.last_time_updated
                self.__update_figure_of_merit(history_route, t_diff)

                # Log the actual figure of merit
                event.obj = (str(history_route), history_route.figure_of_merit)
                self.logger.log_figure_of_merit(self, event)

                # Add the reannouncement penalty
                self.__increase_figure_of_merit(history_route, route, self.rfd.w_penalty,
                                                self.rfd.rfd_ng.ceiling)
                history_route.flaps += 1

                self._print("{} New figure of merit: {}, flapped: {}".format(route, 
                        history_route.figure_of_merit, history_route.flaps))
                event.obj = (str(history_route), history_route.figure_of_merit)
                self.logger.log_figure_of_merit(self, event)

                # Substitute the old route with the new one, with the updated
                # variables
                self.__copy_history_values(route, history_route, False)
                self.rib_handler.history_rib.insert(route)

                # Evaluate if it is possible to use the route
                if route.usable and route.figure_of_merit < self.rfd.cut:
                    self.rib_handler.receive_withdraw(route, event)
                elif not route.usable and route.figure_of_merit < self.rfd.reuse:
                    # I want the route to stay in the history rib because for sure
                    # it has some figure of merit event if under self.rdf.reuse
                    route.usable = True
                    self._print("{} the route is now usable".format(route))
                    event.obj = route
                    self.logger.log_route_reusable(self, event)

                    if route.t_hold_event is not None:
                        route.t_hold_event.interrupt()
                        route.t_hold_event = None
                    if route.reusable_event is not None:
                        route.reusable_event.interrupt()
                        route.reusable_event = None

                    self.rib_handler.receive_withdraw(route, event)
                else:
                    if route.usable:
                        self.rib_handler.receive_withdraw(route, event)
                    route.usable = False
                    if route.t_hold_event is None:
                        self._print("{} SUPPRESSED".format(route))
                        event.obj = route
                        self.logger.log_route_suppressed(self, event)

                        route.first_suppressed_time = self._env.now
                        t_hold_event = Event(self.rfd.t_hold, event.id, Events.END_T_HOLD,
                                              self, self, obj=route)
                        self.event_store.put(t_hold_event)

                    t = self.__calculate_decay_time(route, self.rfd.rfd_ng)
                    self._print("{} will be available again in {}s".format(route, t))
                    reuse_process = Event(t, event.id, Events.ROUTE_REUSABLE,
                                          self, self, obj=route)
                    self.event_store.put(reuse_process)
                    self.rib_handler.history_rib.insert(route)
        else:
            self.rib_handler.receive_withdraw(route, event)

    def route_reusable(self, event: Event) -> None:
        waiting_time = event.event_duration
        route = event.obj
        self._print("If stable {}, will be available again in {}s".format(route, waiting_time))
        try:
            yield self._env.timeout(waiting_time)

            # Check if the route is still in the history
            if not self.rib_handler.history_rib.exists(route):
                self._print("The route is not in the history anymore, someone forgotten " + \
                            "to cancel this event?") 
            else:
                # Take the last version
                route = self.rib_handler.history_rib[route]

            event.obj = route
            self.logger.log_route_reusable(self, event)

            route.reusable_event = None
            t_diff = self._env.now - route.last_time_updated

            if route.t_hold_event is not None:
                route.t_hold_event.interrupt()
                route.t_hold_event = None

            self.__update_figure_of_merit(route, t_diff)
            if route.reachable:
                route.last_time_updated = self._env.now
                route.usable = True

                if route.figure_of_merit > 0:
                    self.rib_handler.history_rib.insert(route)
                self.rib_handler.receive_advertisement(route, event)
            else:
                route.last_time_updated = self._env.now
                route.usable = True
                if route.figure_of_merit > 0:
                    self.rib_handler.history_rib.insert(route)
                self.rib_handler.receive_withdraw(route, event)

            event.obj = (str(route), route.figure_of_merit)
            self.logger.log_figure_of_merit(self, event)
            self._print("{} usable again with a figure of merit of: {}".format(route, 
                route.figure_of_merit))

            # Evaluate the networks
            if not self.__already_scheduled_decision_process:
                proc_time = self.proc_time.get_value()
                decision_process = Event(proc_time, event.id, Events.START_UPDATE_SEND_PROCESS,
                                      self, self, obj=None)
                self.event_store.put(decision_process)
                self.__already_scheduled_decision_process = True

        except simpy.Interrupt as i:
            # Process interrupted, a new message has generated a new figure of merit that
            # needs to be evaluated
            self._print("route updated, reusable event interrupted!")

    def t_hold_experiation(self, event: Event) -> None:
        waiting_time = event.event_duration
        route = event.obj
        self._print("In the worst case the route {} will be available in {}s".format(route, waiting_time))
        try:
            yield self._env.timeout(waiting_time)

            self._print("{} T-hold time experied".format(route))
            # Check if the route is still in the history
            if not self.rib_handler.history_rib.exists(route):
                self._print("The route is not in the history anymore, someone forgottend " + \
                            "to cancel this event?") 
            else:
                # Take the last version
                route = self.rib_handler.history_rib[route]

            event.obj = route
            self.logger.log_t_hold_expiration(self, event)

            route.last_time_updated = self._env.now
            route.figure_of_merit = 0
            route.usable = True
            if route.reusable_event is not None:
                route.reusable_event.interrupt()
                route.reusable_event = None

            route.flaps = 0
            self.rib_handler.history_rib.remove(route)

            event.obj = (str(route), route.figure_of_merit)
            self.logger.log_figure_of_merit(self, event)

            if route.reachable:
                # The route was already reachable so I have to introduce it
                self.rib_handler.receive_advertisement(route, event)
            else:
                # The route was un reachable so I have to insert it as a withdraw
                self.rib_handler.receive_withdraw(route, event)

            # Evaluate the networks
            if not self.__already_scheduled_decision_process:
                proc_time = self.proc_time.get_value()
                decision_process = Event(proc_time, event.id, Events.START_UPDATE_SEND_PROCESS,
                                      self, self, obj=None)
                self.event_store.put(decision_process)
                self.__already_scheduled_decision_process = True
        except simpy.Interrupt as i:
            # Process interrupted, a new message has generated a new figure of merit that
            # needs to be evaluated
            self._print("The route has become available (hopefully), t-hold expiration interrupted!")

    def share_destinations(self, event: Event) -> None:
        """share_destinations.
        Function used to shares all the local destinations
        All the destinations will be introduced in the ADJ-RIB-in and then
        evaluated.
        Will be then required a processing event to evaluate and send
        UPDATE messages if required
        If the signaling option is not active and the withdraw action
        is active will be scheduled a network removement

        :param event: Event that produced the sharing of local destination
        :type event: Event
        :rtype: None
        """
        waiting_time = event.event_duration
        # Waiting for the event to be triggered
        yield self._env.timeout(waiting_time)

        # Reintroduce each network
        # TODO don't introduce all the networks at the same time, make them an event
        for network, dst_event in self._destinations:
            self.new_network(network, dst_event)

        # Evaluate the networks
        if not self.__already_scheduled_decision_process:
            proc_time = self.proc_time.get_value()
            decision_process = Event(proc_time, event.id, Events.START_UPDATE_SEND_PROCESS,
                                  self, self, obj=None)
            self.event_store.put(decision_process)
            self.__already_scheduled_decision_process = True

        # If the configuration permits it then schedule the withdraw of the routes
        if not self.signaling and self.withdraw:
            withdraw_time = self.withdraw_dist.get_value()
            withdraw_event = Event(withdraw_time, None, Events.REMOVE_NETWORKS,
                                   self, self, obj=None)
            self.event_store.put(withdraw_event)

    def remove_destinations(self, event: Event) -> None:
        """remove_destinations.
        Remove all the local destinations of the node and then evaluate
        the changes to the ADJ-RIB-out
        If configured to do so it will schedule a reintroduction

        :param event: Event that generates the destination removement
        :type event: Event
        :rtype: None
        """
        waiting_time = event.event_duration
        # Waiting for the reception
        yield self._env.timeout(waiting_time)

        # Remove each network previously shared
        # TODO don't remove all the network at the same moment, make them an event
        for network, dst_event in self._destinations:
            self.remove_network(network, dst_event)

        # Schedule an evaluation
        if not self.__already_scheduled_decision_process:
            proc_time = self.proc_time.get_value()
            decision_process = Event(proc_time, event.id, Events.START_UPDATE_SEND_PROCESS,
                                  self, self, obj=None)
            self.event_store.put(decision_process)
            self.__already_scheduled_decision_process = True

        # If configured to do so reannounce the destinations
        if not self.signaling and self.reannounce:
            reannouncement_timing = self.reannouncement_dist.get_value()
            redistribute_event = Event(reannouncement_timing, None, Events.REANNOUNCE,
                                        self, self, obj=None)
            self.event_store.put(redistribute_event)

    def add_destination(self, destination: str, path: list, next_hop: str, # pylint: disable=too-many-arguments
            policy_value=0) -> None:
        """add_destination.
        Function used to add a destination to the node not already in route
        format

        :param destination: destination to share
        :type destination: str
        :param path: List of nodes attraversed to reach the destination
        :type path: list
        :param next_hop: Id of the next hop node
        :type next_hop: str
        :param policy_value: Policy value to add to the route, defualt=0
        :rtype: None
        """

        network = ipaddress.ip_network(destination)
        policy = PolicyValue(policy_value)
        new_route = Route(network, path, next_hop, policy_value=policy, mine=True)
        intro_event = Event(0, None, Events.DST_ADD, self, self)
        self._destinations.append((new_route, intro_event))

    def change_state(self, new_state: int):
        """change_state.
            Change the state of a node, test function
        """
        self._print("Change state {} -> {}".format(self._state, new_state))
        self._state = new_state
        self.logger.log_state(self)

    def rx_pkt(self, event):
        """recept.
        Function to handle packet reception

        :param event: receiving event that triggered the reception
        """
        waiting_time = event.event_duration
        # Waiting for the reception
        request = self.processing_res.request()
        yield self._env.timeout(waiting_time) & request
        # Log the reception
        self._print("Start packet reception")
        
        data_rate = self.rate.get_value()
        end_rx = Event(data_rate, event.event_cause, Events.RX, self, self, 
                       obj=(request, event.obj))
        self.event_store.put(end_rx)

    def end_rx_pkt(self, event: Event) -> None:
        request = event.obj[0]
        packet = event.obj[1]
        event.obj = packet
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)

        # Log the end of the reception
        self._print("End packet reception: {}".format(packet))
        self.logger.log_packet_rx(self, event)

        proc_time = self.proc_time.get_value()
        start_pkt_evaluation = Event(proc_time, event.id, Events.START_PKT_EVAL,
                                     self, self, obj=packet)
        self.event_store.put(start_pkt_evaluation)

        # Release the resource
        yield self._env.timeout(self.proc_time.get_value())
        self.processing_res.release(request)

    def start_pkt_eval(self, event: Event) -> None:
        waiting_time = event.event_duration
        # Waiting for the reception
        request = self.processing_res.request()
        yield self._env.timeout(waiting_time) & request

        self._print("Start pkt evalution {}".format(event.obj))

        # Schedule the end of the evaluation
        proc_time = self.proc_time.get_value()
        end_pkt_evaluation = Event(proc_time, event.event_cause, Events.END_PKT_EVAL,
                                   self, self, obj=(request, event.obj))
        self.event_store.put(end_pkt_evaluation)

    def end_pkt_eval(self, event: Event) -> None:
        request = event.obj[0]
        packet = event.obj[1]
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)

        self._print("End pkt evaluation: {}".format(packet))

        # Get the route
        route = packet.content
        route.mine = False
        # If the packet contains an update it will be evaluated
        if packet.packet_type == Packet.UPDATE:
            self.new_network(route, event)
        # If the packet contains a withdrow it will be evaluated by the
        # Withdraw handler
        if packet.packet_type == Packet.WITHDRAW:
            self.remove_network(route, event)

        if not self.__already_scheduled_decision_process:
            proc_time = self.proc_time.get_value()
            decision_process = Event(proc_time, event.event_cause, Events.START_UPDATE_SEND_PROCESS,
                                  self, self, obj=None)
            self.event_store.put(decision_process)
            self.__already_scheduled_decision_process = True

        # Release the resource
        yield self._env.timeout(self.proc_time.get_value())
        self.processing_res.release(request)


    def tx_pkt(self, event):
        """
        tx_pkt.
        Function that transmit the packet to a destination
        :param event: Transmission event
        """
        # Reserve the transmission through a resource
        # to avoid the transmission of messages in reverse order
        # Evaluation of the time necessary for the transmission
        waiting_time = event.event_duration
        request = self.processing_res.request()
        yield self._env.timeout(waiting_time) & request

        self._print("Start TX packet: {}".format(event.obj))
        # Log the transmission
        self.logger.log_start_packet_tx(self, event)

        data_rate = self.rate.get_value()
        end_tx = Event(data_rate, event.event_cause, Events.TX, self, event.destination, 
                       obj=(request, event.obj))
        self.event_store.put(end_tx)

    def end_tx_pkt(self, event: Event) -> None:
        request = event.obj[0]
        packet = event.obj[1]
        dst = event.destination
        event.obj = packet
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)

        # Get the link that will handle the transmission
        link = self._neighbors[dst.id]
        self._print("End TX packet: {}".format(packet))

        # Evaluate the delay necessary for the transfer
        if link.delay is not None:
            delay = link.delay.get_value()
        else:
            delay = self.delay.get_value()
        # Generate the reception event and pass it to the link
        evaluation = self.proc_time.get_value()
        reception_event = Event(evaluation, event.id, Events.START_RX, self, dst,
                                obj=packet, sent_time=self._env.now)
        link.tx(reception_event, delay)
        # Log the transmission
        self.logger.log_packet_tx(self, event)
        # Release the resource
        yield self._env.timeout(self.proc_time.get_value())
        self.processing_res.release(request)

    def __evaluate_advertisement_rib_out(self, event: Event) -> bool:
        """evaluate_advertisement_rib_out.
        Function to evaluate the ADJ-RIB-out if there is an advertisement to share

        :param event: Event that generates the lookup in the ADJ-RIB-out
        :type event: Event
        :rtype: bool Returns if something has been shared
        """
        # Flag to keep track if something has been shared
        share_flag = False
        neigh = event.obj
        neigh_node = self._neighbors[neigh].node
        neigh_id = neigh_node.id
        # Corresponding rib-out table
        adj_rib_out = self.rib_handler.get_rib_out(neigh_id)
        # Check each destination in the ADJ-RIB-out
        for destination in adj_rib_out:
            tmp_route = destination[0]
            for route in destination:
                packet = Packet(Packet.UPDATE, deepcopy(route))
                self._print("rib_out transmitting advertisement {}".format(route))
                # Share the packet and change the flag
                self.send_msg_to_dst(packet, event, neigh_node)
                if not route.mine:
                    share_flag = True
                adj_rib_out.remove(route)
                # TODO check if exists withdraws 
                if self.implicit_withdraw and adj_rib_out.exists_withdraws(route):
                    key = hash(route.addr)
                    for route in adj_rib_out.get_withdraws(key):
                        adj_rib_out.remove_from_withdraws(route)
            # Remove the corresponding element in the table
            del adj_rib_out[tmp_route]
        return share_flag

    def __evaluate_withdraw_rib_out(self, event: Event) -> bool:
        """evaluate_withdraw_rib_out.
        Evaluate the rib out if there are new withdraws to share

        :param event: Event that triggered the lookup
        :type event: Event
        :rtype: bool Returns if something has been shared
        """
        self._print("Check for withdraws")
        share_flag = False
        neigh = event.obj
        neigh_node = self._neighbors[neigh].node
        neigh_id = neigh_node.id
        adj_rib_out = self.rib_handler.get_rib_out(neigh_id)
        withdraw_keys = adj_rib_out.get_withdraws_keys()
        for key in withdraw_keys:
            for route in adj_rib_out.get_withdraws(key):
                if not self.implicit_withdraw or not adj_rib_out.exists(route):
                    packet = Packet(Packet.WITHDRAW, deepcopy(route))
                    self._print("rib_out transmitting withdraw {}".format(route))
                    self.send_msg_to_dst(packet, event, neigh_node)
                    if not route.mine:
                        share_flag = True
                    self._print("Removed route from the list")
                    adj_rib_out.remove_from_withdraws(route)
            if len(adj_rib_out.get_withdraws(key)) == 0:
                adj_rib_out.del_withdraws(key)
        return share_flag

    def __evaluate_routing_table(self) -> None:
        """evaluate_routing_table.
        Evaluate the LOC-RIB to update the routing table

        :rtype: None
        """
        # Add new routes
        for route in self.rib_handler.loc_rib:
            if route not in self.routing_table:
                self.routing_table[route.addr] = route

        # Remove old routes
        route_to_be_removed = []
        for route in self.routing_table:
            if not self.rib_handler.loc_rib.exists(route):
                route_to_be_removed.append(route)

        for route in route_to_be_removed:
            del self.routing_table[route.addr]

    def mrai_waiting(self, event: Event) -> None:
        """mrai_waiting.
        Function used to handle an MRAI cycle, at the end the ADJ-RIB-out will
        be evaluated to see if something changed during the cycle

        :param event: Event that triggered the evaluation
        :type event: Event
        :rtype: None
        """
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)
        self.logger.mrai_cicle(self, event)
        self._print("MRAI cicle ended, now is time to check if there is something to send")
        node_id = event.obj
        link = self._neighbors[node_id]
        # Look if there is something to propagate
        # Send advertisement or withdraw and evaluate if something changed
        w_result = False
        if not self.mrai_withdraw:
            w_result = self.__evaluate_withdraw_rib_out(event)
        a_result = self.__evaluate_advertisement_rib_out(event)
        # If nothing has been shared reset the flag
        # Otherwise wait for another timer cicle
        if a_result or w_result :
            mrai_time = link.mrai
            # If the next mrai is 0 just return becase nothing can be happened
            # in a delta of 0
            if mrai_time == 0:
                link.mrai_not_active()
                return
            self._print("next MRAI cicle in {}".format(mrai_time))
            mrai_event = Event(mrai_time, event.event_cause, Events.MRAI, self, self,
                               obj=node_id)
            self.event_store.put(mrai_event)
        else:
            self._print("Nothing to send")
            link.mrai_not_active()

    def update_send_process(self, event: Event) -> None:
        """update_send_process.
        Function that require to execute the decision process at the rib and
        Require the destination sharing if the MRAI timer permits it
        It will also update the Routing Table

        :param event: Event that triggered the update send process
        :type event: Event
        :rtype: None
        """
        waiting_time = event.event_duration
        request = self.processing_res.request()
        yield self._env.timeout(waiting_time) & request
        self.__already_scheduled_decision_process = False

        # Execute the decision process
        self._print("Start decision process execution")

        data_rate = self.proc_time.get_value()
        end_update_send_process = Event(data_rate, event.event_cause, 
                                        Events.UPDATE_SEND_PROCESS, self, event.destination, 
                                        obj=(request, event.obj))
        self.event_store.put(end_update_send_process)

    def end_update_send_process(self, event: Event) -> None:
        request = event.obj[0]
        event.obj = event.obj[1]
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)

        self._print("Decision process terminated")

        # Evaluate the rib process
        self.rib_handler.decision_process()
        # Evaluate the routing table
        self.__evaluate_routing_table()
        for neigh in self._neighbors:
            link = self._neighbors[neigh]
            if self.mrai_withdraw:
                proc_time = self.proc_time.get_value()
                tmp_mrai_event = Event(proc_time, event.event_cause, Events.MRAI, self, self,
                                       obj=neigh)
                self.__evaluate_withdraw_rib_out(tmp_mrai_event)
            # Require an MRAI execution if there isn't one already triggered
            if not link.mrai_state:
                mrai_time = link.mrai
                mrai_event = Event(mrai_time, event.event_cause, Events.MRAI, self, self,
                                   obj=neigh)
                self.event_store.put(mrai_event)

        self.processing_res.release(request)

    def send_msg_to_dst(self, packet: Packet, event: Event, dst_node) -> None:
        """send_msg_to_dst.
        Function used to send a packet to a specific destination node

        :param packet: Packet to share
        :type packet: Packet
        :param event: Event that triggered the shering
        :type event: Event
        :param dst_node: Destination node of the packet
        :rtype: None
        """
        route = packet.content
        route.add_to_path(self.id)
        route.nh = self.id
        if packet.packet_type == Packet.WITHDRAW:
            self._print("Withdraw for {}".format(dst_node.id))
        elif packet.packet_type == Packet.UPDATE:
            self._print("Advertisement for {}".format(dst_node.id))

        # Get the policy value that is in the routing table
        link = self._neighbors[dst_node.id]
        # Check the link export_policy if it is valid
        route.policy_value = link.test(route.policy_value)
        # If it is not valid jump to the next iteration
        if route.policy_value.value == math.inf:
            self._print("Packet aborted for policies")
            return
        if route.nh == dst_node.id:
            self._print("Packet aborted because the neighbor is my NH \
                         of the route")
            return

        packet_time = self.proc_time.get_value()

        transmission_event = Event(packet_time, event.id,
                                   Events.START_TX, self, dst_node,
                                   obj=packet)
        self.event_store.put(transmission_event)

    def send_msg_to_all(self, packet: Packet, event: Event) -> None:
        """send_msg_to_all.
        Function to send a packet to all the neighbours.
        The packet will be sent only if the route respect the policy value
        of the link and if the neighbour is not the next hop of the route

        :param packet: Packet to send
        :type packet: Packet
        :param event: Cause event
        :type event: Event
        :rtype: None
        """
        for neigh in self._neighbors:
            dst_node = self._neighbors[neigh].node
            self.send_msg_to_dst(packet, event, dst_node)

    def reannounce_handler(self, event):
        """
        Reannouncement function
        used to redistributed a route that was withdrawed before

        :param event: event that triggered the reannouncement
        """
        yield self._env.timeout(event.event_duration)
        packet_time = self.proc_time.get_value()
        transmission_event = Event(packet_time, event.event_cause,
                                   Events.INTRODUCE_NETWORKS, self, self,
                                   obj=None)
        self.event_store.put(transmission_event)

    def handle_event(self): # pylint: disable=arguments-differ
        """handle_event.
        Function to handle events from the store
        """

        while True:
            # Operate only if there is something on the queue
            # Pop the event
            event = yield self.event_store.get()
            # Check if the event is known
            if event.event_type == Events.START_TX:
                self._env.process(self.tx_pkt(event))
            elif event.event_type == Events.TX:
                self._env.process(self.end_tx_pkt(event))
            elif event.event_type == Events.START_RX:
                self._env.process(self.rx_pkt(event))
            elif event.event_type == Events.RX:
                self._env.process(self.end_rx_pkt(event))
            elif event.event_type == Events.REANNOUNCE:
                self._env.process(self.reannounce_handler(event))
            elif event.event_type == Events.START_UPDATE_SEND_PROCESS:
                self._env.process(self.update_send_process(event))
            elif event.event_type == Events.UPDATE_SEND_PROCESS:
                self._env.process(self.end_update_send_process(event))
            elif event.event_type == Events.INTRODUCE_NETWORKS:
                self._env.process(self.share_destinations(event))
            elif event.event_type == Events.REMOVE_NETWORKS:
                self._env.process(self.remove_destinations(event))
            elif event.event_type == Events.MRAI:
                self._env.process(self.mrai_waiting(event))
            elif event.event_type == Events.START_PKT_EVAL:
                self._env.process(self.start_pkt_eval(event))
            elif event.event_type == Events.END_PKT_EVAL:
                self._env.process(self.end_pkt_eval(event))
            elif event.event_type == Events.ROUTE_REUSABLE:
                route = self.rib_handler.history_rib[event.obj]
                if route.reusable_event is not None:
                    self._print("I interrupt the previous reusable event")
                    route.reusable_event.interrupt()
                route_reintroduction = self._env.process(self.route_reusable(event))
                route.reusable_event = route_reintroduction
                self.rib_handler.history_rib.insert(route)
            elif event.event_type == Events.END_T_HOLD:
                route = self.rib_handler.history_rib[event.obj]
                if route.t_hold_event is not None:
                    self._print("I interrupt the previous reusable event (this should not happen)")
                    route.t_hold.interrupt()
                    exit(2)
                route_t_hold = self._env.process(self.t_hold_experiation(event))
                route.t_hold_event = route_t_hold
                self.rib_handler.history_rib.insert(route)
            else:
                raise ValueError("{} is not a valid event type".format(event.event_type))
            # Delete the processed event
            del event

    @property
    def state(self):
        """state."""
        return self._state

    @property
    def id(self): # pylint: disable=invalid-name
        """id."""
        return self._id

    @property
    def neighbors(self):
        """neighbor."""
        return self._neighbors

    def __str__(self):
        """
        Return the node as a human readable object
        """
        res = "Node: {}\n".format(self._id)
        res += "Neighborhood: {}\n".format([n.node.id for n in self._neighbors.values()])
        res += "Destinations queue: "
        res += "\n" + str(self.routing_table)
        res += str(self.rib_handler)
        return res
