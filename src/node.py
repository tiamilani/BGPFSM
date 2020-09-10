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

import sys
import time
import simpy
import bgp_sim
import ipaddress
import math
from copy import copy, deepcopy

sys.path.insert(1, 'util')
from module import Module
from random import Random, randint, expovariate, choice
from event import Event
from events import Events
from packet import Packet
from routingTable import RoutingTable
from route import Route
from distribution import Distribution
from rib import Rib
from policies import PolicyValue


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

    def __init__(self, id, config):
        """__init__.

        :param id: identifier of the node
        :param config: Configuration file
        """
        self._id = id
        # Initial state of the node is IDLE
        self._state = Node.IDLE
        # Simulation environment
        self._env = bgp_sim.sim.Instance().env
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
        # Event handler of a node
        self.reception = self._env.process(self.handle_event())
        # Neighbor of the node
        self._neighbors = {}
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
                
        else:
            self._print("{} - Neighbor {} already in the set".format(self._id, 
                                                                link.node.id))
            exit(1)

    def evaluate_signaling_event(self, elem, route):
        if elem == "A":
            proc_time = self.reannouncement_dist.get_value()
            event = Event(proc_time, None, Events.NEW_DST, self, self, 
                          obj=route)
        elif elem == "W":
            withdraw_packet = Packet(Packet.WITHDRAW, route)
            withdraw_time = self.withdraw_dist.get_value()
            event = Event(withdraw_time, None, Events.WITHDRAW, self, self, 
                          obj=withdraw_packet)
        else:
            raise ValueError("Elem {} not accepted in signaling, accepted \
                              simbols: {}".format(elem, 
                                self.signaling_accepted_simbols))
        return event


    def force_share_dst(self):
        for route in self.routing_table:
            # Create a new destination event for each route in the routing
            # Table that needs to be shared
            if not self.signaling:
                proc_time = self.proc_time.get_value()
                new_dst_event = Event(proc_time, None, Events.NEW_DST, self, self,
                                      route)
                self.event_store.put(new_dst_event)
            else:
                time = 0
                for elem in self.signaling_sequence:
                    event = self.evaluate_signaling_event(elem, route)
                    self._print("New event to signal t: {}, delay: {}".format(
                                time, event.event_duration))
                    time += event.event_duration 
                    event.event_duration = time
                    self.event_store.put(event)

    def new_network(self, route: Route, event: Event, share=True):
        old_best = deepcopy(self.rib[route.addr])
        new_best = self.rib.insert(route.addr, route, event=event,
                                   implicit_withdraw=self.implicit_withdraw)
        # Evaluate if the new route is the new best route for the destiantion
        if new_best != None and new_best != old_best:
            # If it is the new best route insert it in the routing table and 
            # Log the event
            self.routing_table[route.addr] = route
            self._print("New route in the routing table {}".format(route))
            rt_change_event = Event(0, event.id, Events.RT_CHANGE, 
                                    self, self, obj=route)
            self.logger.log_rt_change(self, rt_change_event)
            
            if share:
                proc_time = self.proc_time.get_value()
                new_dst_event = Event(proc_time, event.id, Events.NEW_DST, 
                                      self, self, obj=route)
                self.event_store.put(new_dst_event)

    def add_destination(self, destination, path, nh, event=None, policy_value=0,
                        share=False):
        """
        Function that adds a destination to the data structure
        that manage destinations that needs to be shared inside the node

        :param destination: destination that is originated by the node
        :param path: path to the destination
        :param nh: nh for the route
        """
        network = ipaddress.ip_network(destination)
        policy = PolicyValue(policy_value)
        r = Route(network, path, nh, policy_value=policy, mine=True)
        intro_event = Event(0, None, Events.DST_ADD, self, self)
        self.new_network(r, intro_event, share=share)

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
            withdraw_packet = Packet(Packet.WITHDRAW, route)
            withdraw_event = Event(0, event.id, Events.WITHDRAW, 
                                   self, self, obj=withdraw_packet)
            self.event_store.put(withdraw_event)

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


    def share_dst(self, event):
        """share_dst.
        Share a destiantion to all the neighbors that are in destination queue

        :param event: event that trigger the sharing of the destination
        """
        waiting_time = event.event_duration
        yield self._env.timeout(waiting_time)
        dst = event.obj
        
        for neigh in self._neighbors:
            link = self._neighbors[neigh]
            dst_node = self._neighbors[neigh].node
            self._print("I have to send {} to {}".format(dst, neigh))
            route = deepcopy(dst)

            # Check the link export_policy if it is valid 
            route.policy_value = link.test(route.policy_value) 
            # If it is not valid jump to the next iteration
            if route.policy_value.value == math.inf:
                continue
            if route.nh == dst_node.id:
                continue

            # Add the self id to the path and nh field
            route.add_to_path(self._id)
            route.nh = self._id

            # Create the event
            packet = Packet(Packet.UPDATE, route)
            interrarival = self.rate.get_value()
            transmission_event = Event(interrarival, event.event_cause,
                                       Events.TX, self, dst_node, obj=packet)
            # Send the event to the handler
            self.event_store.put(transmission_event)

        if dst.mine and not self.signaling and self.withdraw:
            # Generate the withdraw event
            withdraw_packet = Packet(Packet.WITHDRAW, dst)
            withdraw_time = self.withdraw_dist.get_value()
            withdraw_event = Event(withdraw_time, event.event_cause,
                                   Events.WITHDRAW, self, self, 
                                   obj=withdraw_packet)
            self.event_store.put(withdraw_event)

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

        if new_best == None:
            del self.routing_table[route.addr]
            rt_change_event = Event(0, event.event_cause, Events.RT_CHANGE,
                                    self, self, obj=Route(route.addr, [], None))
            self.logger.log_rt_change(self, rt_change_event)
        elif new_best != old_best:
            self.routing_table[route.addr] = new_best
            rt_change_event = Event(0, event.event_cause, Events.RT_CHANGE,
                                    self, self, obj=new_best)
            self.logger.log_rt_change(self, rt_change_event)
        elif new_best == old_best:
            self._print("Best route not changed, nothing to share")
            return

        # Send the packet to the neighborhod
        if new_best == None:
            for neigh in self._neighbors:
                route_copy = deepcopy(packet.content)
                # Generate the withdraw packet
                route_copy.add_to_path(self._id)
                route_copy.nh = self._id
                dst_node = self._neighbors[neigh].node
                self._print("Withdraw for {}".format(dst_node.id))

                # Get the policy value that is in the routing table
                link = self._neighbors[dst_node.id]
                # Check the link export_policy if it is valid 
                route_copy.policy_value = link.test(route_copy.policy_value) 
                # If it is not valid jump to the next iteration
                if route_copy.policy_value.value == math.inf:
                    self._print("Withdraw aborted for policies")
                    continue
                if route.nh == dst_node.id:
                    self._print("Withdraw aborted because the neighbor is my NH of the withdraw")
                    continue

                withdraw_packet = Packet(Packet.WITHDRAW, route_copy)
                withdraw_time = self.rate.get_value()

                transmission_event = Event(withdraw_time, event.event_cause,
                                            Events.TX, self, dst_node,
                                            obj=withdraw_packet)
                self.event_store.put(transmission_event)

        if new_best is not None:
            for neighbor in self._neighbors:
                self._print("I have a new best to send")
                update_route = deepcopy(new_best)
                update_route.add_to_path(self._id)
                update_route.nh = self._id
                dst_node = self._neighbors[neighbor].node
                self._print("Update for {}".format(dst_node.id))

                # Get the policy value that is in the routing table
                link = self._neighbors[dst_node.id]
                # Check the link export_policy if it is valid 
                update_route.policy_value = link.test(update_route.policy_value) 
                # If it is not valid jump to the next iteration
                if update_route.policy_value.value == math.inf:
                    continue
                if new_best.nh == dst_node.id:
                    continue

                update_packet = Packet(Packet.UPDATE, update_route)
                update_time = self.rate.get_value()

                transmission_event = Event(update_time, event.event_cause, 
                                           Events.TX, self, dst_node, 
                                           obj=update_packet)
                self.event_store.put(transmission_event)

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
        net = event.obj
        self._print("I have to reintroduce {}".format(net))
        self.add_destination(net, [], None, share=True)

    def handle_event(self):
        """handle_event.
        Function to handle events from the store
        """

        while True:
            # Operate only if there is something on the queue
            # Pop the event
            event = yield self.event_store.get()
            # Check if the event is known
            if event.event_type == Events.STATE_CHANGE:
                # If the event is a state changer change the state
                packet = event.obj
                self._env.process(self.change_state(1))
            if event.event_type == Events.TX:
                self._env.process(self.tx_pkt(event))
            if event.event_type == Events.RX:
                self._env.process(self.rx_pkt(event))
            if event.event_type == Events.NEW_DST:
                self._env.process(self.share_dst(event))
            if event.event_type == Events.WITHDRAW:
                self._env.process(self.program_withdraw(event))
            if event.event_type == Events.REANNOUNCE:
                self._env.process(self.reannounce_handler(event))
            # Delete the processed event
            del event

    @property
    def state(self):
        """state."""
        return self._state

    @property
    def id(self):
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
        return res
