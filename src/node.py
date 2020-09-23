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
from routingTable import RoutingTable
from route import Route
from distribution import Distribution
from rib import Rib, BGP_RIB_handler
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
        # Rib table, this table represent all the routing knowledge
        # present in the node, plus routes that are not the best
        self.rib = Rib(self._id, self.logger)
        self.rib_handler = BGP_RIB_handler(self._id, self.logger)
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
        # Implicit withdraw flag
        self.implicit_withdraw = config.get_param(Node.PAR_IMPLICIT_WITHDRAW) in ("True", "true")
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
        self.tx_res = simpy.Resource(self._env, capacity=1)

    def _print(self, msg):
        """_print.
        Print a message from the node
        evaluate the verbose level before printing a message

        :param msg: Message that needs to be printed on sysout
        """
        if self.verbose:
            print("{}-{} ".format(self._env.now, self._id) + msg)

    def add_neighbor(self, link):
        """
        Add a neighbor to the set of neighbors
        If the neighbor is already in the set it throws an error
        and terminate

        :param link: link that has to be added
        """
        # Evaluate if the link is already present
        if link.id not in self._neighbors:
            self._neighbors[link.node.id] = link
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
        :param route: Route to share or withdraw
        :type route: Route
        :rtype: Event

        :raise ValueError: When is passed an element that is not a valid signal
        """
        if elem == "A":
            proc_time = self.reannouncement_dist.get_value()
            event = Event(proc_time, None, Events.INTRODUCE_NETWORKS, self, self,
                          obj=None)
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
        # self.rib_handler.decision_process()
        # self.evaluate_routing_table()
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

    def new_network(self, route: Route, event: Event, share=True) -> None:
        """new_network.
        Function used to add a new route, it will be evaluated for the
        insertion in the rib and it will be then evaluated for the Routing table

        :param route: Route to evaluate
        :type route: Route
        :param event: Cause event for the evaluation
        :type event: Event
        :param share: The network should be shared if it's the new best? (default=True)
        :rtype: None
        """
        self.rib_handler.receive_advertisement(route, event)

    def remove_network(self, route: Route, event: Event, share=True) -> None:
        """remove_network.
        Function used to add a new route, it will be evaluated for the
        insertion in the rib and it will be then evaluated for the Routing table

        :param route: Route to evaluate
        :type route: Route
        :param event: Cause event for the evaluation
        :type event: Event
        :param share: The network should be shared if it's the new best? (default=True)
        :rtype: None
        """
        self.rib_handler.receive_withdraw(route, event)

    def share_destinations(self, event):
        waiting_time = event.event_duration
        # Waiting for the reception
        yield self._env.timeout(waiting_time)
        
        for network, event in self._destinations:
            self.new_network(network, event)

        proc_time = self.proc_time.get_value()
        decision_process = Event(proc_time, event.id, Events.UPDATE_SEND_PROCESS,
                              self, self, obj=None)
        self.event_store.put(decision_process)
        if not self.signaling and self.withdraw:
            withdraw_time = self.withdraw_dist.get_value()
            withdraw_event = Event(withdraw_time, None, Events.REMOVE_NETWORKS,
                                   self, self, obj=None)
            self.event_store.put(withdraw_event)

    def remove_destinations(self, event):
        waiting_time = event.event_duration
        # Waiting for the reception
        yield self._env.timeout(waiting_time)
        
        for network, event in self._destinations:
            self.remove_network(network, event)

        proc_time = self.proc_time.get_value()
        decision_process = Event(proc_time, event.id, Events.UPDATE_SEND_PROCESS,
                              self, self, obj=None)
        self.event_store.put(decision_process)

        if not self.signaling and self.reannounce:
            reannouncement_timing = self.reannouncement_dist.get_value()
            redistribute_event = Event(reannouncement_timing, None, Events.REANNOUNCE,
                                        self, self, obj=None)
            self.event_store.put(redistribute_event)

    def add_destination(self, destination: str, path: list, next_hop: str, # pylint: disable=too-many-arguments
            policy_value=0, share=False) -> None:
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
        :param share: Sharing flag, default=True, if false the route will
                      be added but not shared
        :rtype: None
        """

        network = ipaddress.ip_network(destination)
        policy = PolicyValue(policy_value)
        new_route = Route(network, path, next_hop, policy_value=policy, mine=True)
        intro_event = Event(0, None, Events.DST_ADD, self, self)
        # self.new_network(new_route, intro_event, share=share)
        self._destinations.append((new_route, intro_event))

    def change_state(self, waiting_time):
        """change_state.
            Change the state of a node, test function
        """
        yield self._env.timeout(waiting_time)
        self._state = Node.STATE_CHANGING
        self.logger.log_state(self)

    def rx_pkt(self, event):
        """recept.
        Function to handle packet reception

        :param event: receiving event that triggered the reception
        """
        packet = event.obj
        waiting_time = event.event_duration
        # Waiting for the reception
        yield self._env.timeout(waiting_time)
        # Log the reception
        self._print("Packet_RX: " + str(packet))
        self.logger.log_packet_rx(self, event)
        # Get the route
        route = packet.content
        route.mine = False
        # If the packet contains an update it will be evaluated
        if packet.packet_type == Packet.UPDATE:
            self.new_network(route, event)
        # If the packet contains a withdrow it will be evaluated by the
        # Withdraw handler
        if packet.packet_type == Packet.WITHDRAW:
            # self.withdraw_handler(event, packet)
            route = deepcopy(packet.content)
            self.rib_handler.receive_withdraw(route, event)
            withdraw_packet = Packet(Packet.WITHDRAW, route)
            withdraw_event = Event(0, event.id, Events.WITHDRAW,
                                   self, self, obj=withdraw_packet)
            self.event_store.put(withdraw_event)
        proc_time = self.proc_time.get_value()
        decision_process = Event(proc_time, event.id, Events.UPDATE_SEND_PROCESS,
                              self, self, obj=None)
        self.event_store.put(decision_process)

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
        request = self.tx_res.request()
        yield self._env.timeout(waiting_time) & request
        dst = event.destination
        packet = event.obj
        # Get the link that will handle the transmission
        link = self._neighbors[dst.id]
        self._print("Packet_TX: " + str(packet))
        # Evaluate the delay necessary for the transfer
        if link.delay is not None:
            delay = link.delay.get_value()
        else:
            delay = self.delay.get_value()
        # Generate the reception event and pass it to the link
        evaluation = self.proc_time.get_value()
        reception_event = Event(evaluation, event.id, Events.RX, self, dst,
                                obj=packet, sent_time=self._env.now)
        link.tx(reception_event, delay)
        # Log the transmission
        self.logger.log_packet_tx(self, event)
        # Release the resource
        wait = self.proc_time.get_value()
        yield self._env.timeout(wait)
        self.tx_res.release(request)

    def evaluate_advertisement_rib_out(self, event: Event) -> bool:
        share_flag = False
        neigh = event.obj
        neigh_node = self._neighbors[neigh].node
        neigh_id = neigh_node.id
        adj_rib_out = self.rib_handler.get_rib_out(neigh_id)
        for destination in adj_rib_out:
            tmp_route = destination[0]
            for route in destination:
                packet = Packet(Packet.UPDATE, deepcopy(route))
                self._print("rib_out transmitting advertisement {}".format(route))
                self.send_msg_to_dst(packet, event, neigh_node)
                share_flag = True
                adj_rib_out.remove(route)
            del adj_rib_out[tmp_route]
        return share_flag

    def evaluate_withdraw_rib_out(self, event: Event):
        share_flag = False
        neigh = event.obj
        neigh_node = self._neighbors[neigh].node
        neigh_id = neigh_node.id
        adj_rib_out = self.rib_handler.get_rib_out(neigh_id)
        for route in adj_rib_out.get_withdraws():
            packet = Packet(Packet.WITHDRAW, deepcopy(route))
            self._print("rib_out transmitting withdraw {}".format(route))
            self.send_msg_to_dst(packet, event, neigh_node)
            share_flag = True
            adj_rib_out.remove_from_withdraws(route)
        return share_flag

    def evaluate_routing_table(self):
        for route in self.rib_handler.loc_rib:
            if route not in self.routing_table:
                self.routing_table[route.addr] = route

        route_to_be_removed = []
        for route in self.routing_table:
            if not self.rib_handler.loc_rib.exists(route):
                route_to_be_removed.append(route)

        for route in route_to_be_removed:
            del self.routing_table[route.addr]

    def mrai_waiting(self, event):
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)
        node_id = event.obj
        link = self._neighbors[node_id]
        # Look if there is something to propagate
        self._print("Required decision process")
        self.rib_handler.decision_process()
        self.evaluate_routing_table()
        a_result = self.evaluate_advertisement_rib_out(event)
        w_result = self.evaluate_withdraw_rib_out(event)
        # If nothing has been shared reset the flag
        # Otherwise wait for another timer cicle
        if a_result or w_result:
            mrai_time = link.mrai
            self._print("I sent something, so I set another MRAI to {}".format(mrai_time))
            mrai_event = Event(mrai_time, event.id, Events.MRAI, self, self,
                               obj=node_id)
            self.event_store.put(mrai_event)
        else:
            self._print("Nothing has been sent, so I deactivate MRAI")
            link.mrai_not_active()

    def update_send_process(self, event):
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)
        self._print("update send process")
        # propagation that thakes into account MRAI
        for neigh in self._neighbors:
            link = self._neighbors[neigh]
            if not link.mrai_state:
                mrai_time = link.mrai
                self._print("Mrai not active, mrai time: {}".format(mrai_time))
                mrai_event = Event(mrai_time, event.id, Events.MRAI, self, self,
                                   obj=neigh)
                self.event_store.put(mrai_event)

    # TODO remove
    def share_dst(self, event):
        """share_dst.
        Share a destiantion to all the neighbors
        If the destination is originated by this node and the withdraw flag
        is active a withdraw will also be triggered

        :param event: event that triggered the sharing of the destination
        """
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)
        dst = event.obj

        route = deepcopy(dst)
        # Add the self id to the path and nh field
        route.add_to_path(self._id)
        route.nh = self._id
        packet = Packet(Packet.UPDATE, route)
        self.send_msg_to_all(packet, event)

        if dst.mine and not self.signaling and self.withdraw:
            # Generate the withdraw event
            withdraw_packet = Packet(Packet.WITHDRAW, dst)
            withdraw_time = self.withdraw_dist.get_value()
            withdraw_event = Event(withdraw_time, event.event_cause,
                                   Events.WITHDRAW, self, self,
                                   obj=withdraw_packet)
            self.event_store.put(withdraw_event)

    def send_msg_to_dst(self, packet: Packet, event: Event, dst_node) -> None:
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

        packet_time = self.rate.get_value()

        transmission_event = Event(packet_time, event.event_cause,
                                   Events.TX, self, dst_node,
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
            # self.send_msg_to_dst(packet, event, dst_node)

    # TODO remove
    def program_withdraw(self, event):
        """program_withdraw.
        Function used to program a withdraw of a previusly
        shared destination

        :param event: event that generates the withdraw, used to
            get the delay time and the route that needs to be withdrawed
        """
        # Wait the time defined by the withdraw distribution
        yield self._env.timeout(event.event_duration)

        # Get the route
        packet = event.obj
        route = packet.content
        self._print("Route to withdraw: " + str(route))

        # Delete the route from the routing table and the rib
        old_best = self.rib[route.addr]
        if self.rib.contains(route.addr, route):
            change_event = Event(0, event.event_cause, Events.RIB_CHANGE,
                    None, None)
            change_event.id = event.event_cause
            self.rib.remove(route.addr, route, event=change_event)
        else:
            self._print("Rib does not contains: " + str(route))
            return
        new_best = self.rib[route.addr]

        if new_best is None:
            del self.routing_table[route.addr]
            rt_change_event = Event(0, event.event_cause, Events.RT_CHANGE,
                                    self, self, obj=Route(route.addr, [], None))
            self.logger.log_rt_change(self, rt_change_event)

            # Send a withdraw for the route
            route_copy = deepcopy(packet.content)
            route_copy.add_to_path(self._id)
            route_copy.nh = self._id
            withdraw_packet = Packet(Packet.WITHDRAW, route_copy)
            self.send_msg_to_all(withdraw_packet, event)
        elif new_best != old_best:
            self.routing_table[route.addr] = new_best
            rt_change_event = Event(0, event.event_cause, Events.RT_CHANGE,
                                    self, self, obj=new_best)
            self.logger.log_rt_change(self, rt_change_event)

            # Send an update with the new best
            update_route = deepcopy(new_best)
            update_route.add_to_path(self._id)
            update_route.nh = self._id
            update_packet = Packet(Packet.UPDATE, update_route)
            self.send_msg_to_all(update_packet, event)
        elif new_best == old_best:
            self._print("Best route not changed, nothing to share")
            return

        # Check if it's needed a redistribution
        if not self.signaling and self.reannounce and packet.content.mine == 0:
            reannouncement_timing = self.reannouncement_dist.get_value()
            redistribute_event = Event(reannouncement_timing, None, Events.REANNOUNCE,
                                        self, self, obj=route.addr)
            self.event_store.put(redistribute_event)

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
            if event.event_type == Events.TX:
                self._env.process(self.tx_pkt(event))
            elif event.event_type == Events.RX:
                self._env.process(self.rx_pkt(event))
            elif event.event_type == Events.NEW_DST:
                self._env.process(self.share_dst(event))
            elif event.event_type == Events.WITHDRAW:
                self._env.process(self.program_withdraw(event))
            elif event.event_type == Events.REANNOUNCE:
                self._env.process(self.reannounce_handler(event))
            elif event.event_type == Events.UPDATE_SEND_PROCESS:
                self._env.process(self.update_send_process(event))
            elif event.event_type == Events.INTRODUCE_NETWORKS:
                self._env.process(self.share_destinations(event))
            elif event.event_type == Events.REMOVE_NETWORKS:
                self._env.process(self.remove_destinations(event))
            elif event.event_type == Events.MRAI:
                self._env.process(self.mrai_waiting(event))
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
        res += str(self.rib)
        res += str(self.rib_handler)
        return res
