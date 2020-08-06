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
# Copyright (C) 2016 Michele Segata <segata@ccs-labs.org>

# Modified by Mattia Milani
# Copyright (C) 2020 Mattia Milani <mattia.milani@studenti.unitn.it>

import sys

sys.path.insert(1, '..')
import bgp_sim
from events import Events


class Log:
    """
    Defines data logging utilities
    """

    def __init__(self, output_file, log_routing_change=True,
            log_packets=False, log_states=False):
        """
        Constructor.
        :param output_file: output file name. will be overwritten if already
        existing
        :param log_packets: enable/disable logging of packets
        :param log_states: enable/disable logging of the state of nodes
        """
        self.sim = bgp_sim.sim.Instance()
        self.log_file = open(output_file, "w")
        self.log_file.write("event,time,node,value\n")
        self.log_packets = log_packets
        self.log_states = log_states
        self.log_routing_change = log_routing_change

    def __delete__(self, instance):
        self.log_file.close()

    def log_rt_change(self, node, route):
        """
        Logs the result of a routing table change
        :param route: the new route in the routing table
        """
        if self.log_routing_change:
            self.log_file.write("{},{},{},{}\n".format(Events.RT_CHANGE,
                                            self.sim.env.now, node.id,
                                            route))

    def log_packet_tx(self, node, packet):
        """
        Logs a packet tx.
        :param node: source node
        :param packet: the packet to log
        """
        if self.log_packets:
            self.log_file.write("{},{},{},{}\n".format(Events.TX,
                                                self.sim.env.now, 
                                                node.id, 
                                                packet))
    
    def log_packet_RX(self, node, packet):
        """
        Logs a packet tx.
        :param node: source node
        :param packet: the packet to log
        """
        if self.log_packets:
            self.log_file.write("{},{},{},{}\n".format(Events.RX,
                                                self.sim.env.now, 
                                                node.id, 
                                                packet))

    def log_state(self, node):
        """
        Logs the state of a particular node
        :param node: node
        :param state: state of the node
        """
        if self.log_states:
            self.log_file.write("{},{},{},{}\n".format(Events.STATE_CHANGE,
                                                    self.sim.env.now, 
                                                    node.id, node.state))
