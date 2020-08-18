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
    

    def __init__(self, id, config):
        """__init__.

        :param id: identifier of the node
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
        # Destinations queue, this queue contains the destinations
        # That are not yet distributed to neighbors
        # The structure is a dictionary, the key is the destination
        # And the object is a list of neighbor that didn't receive from
        # us the destination yet
        self.destination_queue = {}
        # Routing table, This table represent the routing knowledge
        # actually present in the nod
        self.routing_table = RoutingTable()
        # Random used to generate traffic
        self.g = Random(time.time() * hash(self._id))
        # Event handler of a node
        self.reception = self._env.process(self.handle_event())
        # Neighbor of the node
        self._neighbors = {}
        # Distributions used inside the node
        self.rate = Distribution(config.get_param(Node.PAR_DATARATE))
        self.proc_time = Distribution(config.get_param(Node.PAR_PROC_TIME))
        self.delay = Distribution(config.get_param(Node.PAR_DELAY))

    def _print(self, msg):
        """_print.
        Print evaluate the verbose level before printing a message

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
        if link.id not in self._neighbors:
            self._neighbors[link.node.id] = link
            for route in self.routing_table:
                dst = route.addr
                if dst in self.destination_queue:
                    self.destination_queue[dst].append(link.node.id)
                else:
                    self.destination_queue[dst] = [link.node.id]

                if route.nh in self.destination_queue[dst]:
                    self.destination_queue[dst].remove(route.nh)

                """rm_list = []
                for l in self.destination_queue[dst]:
                    if self._neighbors[l].node.id == route.nh:
                        rm_list.append(l)
                for elem in rm_list:
                    self.destination_queue[dst].remove(elem)"""

                if len(self.destination_queue[dst]) > 0:
                    proc_time = self.proc_time.get_value()
                    new_dst_event = Event(proc_time, Events.NEW_DST, self, self)
                    self.event_store.put(new_dst_event)

        else:
            print("{} - Neighbor {} already in the set".format(self._id, link.node.id))
            exit(1)

    def add_destination(self, destination, path, nh):
        """
        Function that adds a destination to the data structure
        that manage destinations that needs to be shared inside the node

        :param destination: destination that is originated by the node
        """
        network = ipaddress.ip_network(destination)
        r = Route(network, path, nh)

        if self.routing_table.insert(network, r) != None:
            self.logger.log_rt_change(self, r)

            if len(self._neighbors.keys()) > 0:
                self.destination_queue[network] = list(self._neighbors.keys())
            else:
                self.destination_queue[network] = []
            
            if nh in self.destination_queue[network]:
                self.destination_queue[network].remove(nh)

            if len(self.destination_queue[network]) > 0:
                new_dst_event = Event(0.1, Events.NEW_DST, self, self)
                self.event_store.put(new_dst_event)
            else:
                del self.destination_queue[network]

    def change_state(self, packet):
        """change_state.
            Change the state of a node, test function
        """
        self._print("changing state thanks to packet: " + str(packet.id))
        self._state = Node.STATE_CHANGING
        self.logger.log_state(self)

    def rx_pkt(self, packet):
        """recept.
        Function to handle packet reception 

        :param packet: packet received 
        """
        self._print("Packet_RX: " + str(packet))
        route = packet.content
        self.add_destination(route.addr, route.path, route.nh)

    def tx_pkt(self, event):
        dst = event.destination
        packet = event.obj
        link = self._neighbors[dst.id]
        self._print("Packet_TX: " + str(packet))
        # Create the event for the reception
        if link.delay is not None:
            delay = link.delay.get_value()
        else: 
            delay = self.delay.get_value()
        reception_event = Event(0, Events.RX, self, dst, obj=packet, 
                                sent_time=self._env.now)
        #dst.event_store.put(reception_event)
        link.tx(reception_event, delay)

    def share_dst(self):
        del_dst = []
        for dst in self.destination_queue:
            del_neigh = []
            for neigh in self.destination_queue[dst]:
                # self._print("I should send {} to {}".format(dst,neigh))
                route = deepcopy(self.routing_table[dst])
                route.add_to_path(self._id)
                route.nh = self._id

                # Create the event
                packet = Packet(route)
                dst_node = self._neighbors[neigh].node
                # self._print("dst node: " + str(neigh))
                interrarival = self.rate.get_value()
                transmission_event = Event(interrarival, Events.TX, 
                                    self, dst_node, obj=packet)
                # Send the event to the handler
                self.event_store.put(transmission_event)
                # self._print("Required packet transmission pkt_id: " + str(packet.id))

                del_neigh.append(neigh)
            for del_elem in del_neigh:
                self.destination_queue[dst].remove(del_elem)
            if len(self.destination_queue[dst]) == 0:
                del_dst.append(dst)
        for del_elem in del_dst:
            del self.destination_queue[del_elem]

    def handle_event(self):
        """handle_event.
        Function to handle events from the queue
        """

        while True:
            # Operate only if there is something on the queue
            # Pop the event
            event = yield self.event_store.get()
            waiting_time = event.event_duration
            if event.event_type == Events.RX:
                waiting_time = event.event_duration - (self._env.now - event.sent_time)
                if waiting_time < 0:
                    waiting_time = self.proc_time.get_value()
            # Wait the corresponding time to process the event
            yield self._env.timeout(waiting_time)
            # Check if the event is known
            if event.event_type == Events.STATE_CHANGE:
                # If the event is a state changer change the state
                packet = event.obj
                self.change_state(packet)
                del packet
            if event.event_type == Events.TX:
                self.tx_pkt(event)
            if event.event_type == Events.RX:
                self.rx_pkt(event.obj)
            if event.event_type == Events.NEW_DST:
                self.share_dst()
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
        for dst in self.destination_queue:
            res += "{}-{} ".format(str(dst), str(self.destination_queue[dst]))
        res += "\n" + str(self.routing_table)
        return res
