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

sys.path.insert(1, 'util')
from module import Module
from random import Random, randint, expovariate, choice
from event import Event
from events import Events
from packet import Packet


class Node(Module):
    """Node.
    Class to manage node inside the simulation
    """

    # States of the node 
    IDLE = 0
    STATE_CHANGING = 1

    def __init__(self, id):
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
        # Message queue of a node
        self.queue = []
        # Events queue, events that needs to be handle by the node
        self.event_queue = []
        # Event to trigger when there is a new event to handle
        self.new_event = self._env.event()
        # Random used to generate traffic
        self.g = Random(time.time() * hash(self._id))
        # Event to trigger the management of a reception
        self.rec_ev = self._env.event()
        # Basic processing unit of a node, this unit generate traffic
        # The generation rate is 0.2
        self.proc = self._env.process(self.run(0.2))
        # Event handler of a node
        self.reception = self._env.process(self.handle_event())
        # Neighbor of the node
        self._neighbors = {}

    def _print(self, msg):
        """_print.
        Print evaluate the verbose level before printing a message

        :param msg: Message that needs to be printed on sysout
        """
        if self.verbose:
            print("{}-{} ".format(self._env.now, self._id) + msg)

    def add_neighbor(self, node):
        """
        Add a neighbor to the set of neighbors
        If the neighbor is already in the set it throws an error 
        and terminate
        
        :param node: node that has to be setted
        """
        if node.id not in self._neighbors:
            self._neighbors[node.id] = node
        else:
            print("{} - Neighbor {} already in the set".format(self._id, node.id))
            exit(1)

    def run(self, rate):
        """run.

        :param rate: Message rate
        """
        while True:
            # Wait for the corresponding rate with an exponential distribution
            yield self._env.timeout(self.g.expovariate(rate))
            # Create the event
            packet = Packet("packet content")
            # Chose a neighbor randomly
            dst = choice(list(self._neighbors.values()))
            transmission_event = Event(1, Events.TX, self, dst, obj=packet)
            # Send the event to the handler
            self.event_queue.insert(0, transmission_event)
            self._print("Required packet transmission pkt_id: " + str(packet.id))
            self.new_event.succeed()
            self.new_event = self._env.event()

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
        self._print("Packet received: " + str(packet.id))

    def tx_pkt(self, event):
        dst = event.destination
        packet = event.obj
        self._print("Packet transmission: " + str(packet.id))
        # Create the event for the reception
        reception_event = Event(1, Events.RX, self, dst, obj=packet)
        dst.event_queue.insert(0, reception_event)
        dst.new_event.succeed()
        dst.new_event = self._env.event()


    def handle_event(self):
        """handle_event.
        Function to handle events from the queue
        """

        while True:
            # Operate only if there is something on the queue
            if len(self.event_queue) > 0:
                # Pop the event
                event = self.event_queue.pop()
                # Wait the corresponding time to process the event
                yield self._env.timeout(event.event_duration)
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
                # Delete the processed event
                del event
            # If there are no events in the queue pass to the idle state
            # and wait for the next event
            if len(self.event_queue) == 0:
                self._state = Node.IDLE
                self.logger.log_state(self)
                yield self.new_event

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
        res += "Neighborhood: {}".format([n.id for n in self._neighbors.values()])
        return res
