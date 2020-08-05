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
sys.path.insert(1, 'util')

import simpy
import bgp_sim
from module import Module
from random import Random, randint, expovariate, choice
import time
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
        #FIXME don't use a list but use a queue structure
        self.queue = []
        # Random used to generate traffic
        self.g = Random(time.time()*hash(self._id))
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

        :param msg: Message that needs to be printed on sysout
        """
        if self.verbose:
            print("{}-{} ".format(self._env.now, self._id) + msg)

    def add_neighbor(self, node):
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
            dst = choice(list(self._neighbors.values()))
            change_state_evt = Event(2, Events.STATE_CHANGE, self, dst, obj=packet)
            # Send the event
            dst.recept(change_state_evt)

    def change_state(self, packet):
        """change_state.
            Change the state of a node, test function
        """
        self._print("changing state thanks to packet: " + str(packet.id))
        self._state = Node.STATE_CHANGING
        self.logger.log_state(self)

    def recept(self, event):
        """recept.
        Function to handle input events

        :param event: Event that needs to be handled
        """
        # Insertion of the event
        self.queue.insert(0, event)
        self._print("event received")
        # Unlock the event hendler in the case it is locked with an empty queue
        self.rec_ev.succeed()
        # Regenerate the event for the reception
        self.rec_ev = self._env.event()

    def handle_event(self):
        """handle_event.
        Function to handle events from the queue
        """

        while True:
            # Operate only if there is something on the queue
            if len(self.queue) > 0:
                # Pop the event
                event = self.queue.pop()
                # Wait the corresponding time to process the event
                yield self._env.timeout(event.event_duration)
                # Check if the event is known
                if event.event_type == Events.STATE_CHANGE:
                    # If the event is a state changer change the state
                    packet = event.obj
                    self.change_state(packet)
                # Delete the processed event
                del event
                del packet
            # If there are no events in the queue pass to the idle state
            # and wait for the next event
            if len(self.queue) == 0:
                self._state = Node.IDLE
                self.logger.log_state(self)
                yield self.rec_ev

    @property
    def state(self):
        """state."""
        return self._state

    @property
    def id(self):
        """id."""
        return self._id

    @property
    def neighbors():
        """neighbor."""
        return self._neighbors

    def __str__(self):
        """
        Return the node as a human readable object
        """
        res = "Node: {}\n".format(self._id)
        res += "Neighborhood: {}".format([n.id for n in self._neighbors.values()])
        return res
