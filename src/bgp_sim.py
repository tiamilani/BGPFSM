#!/usr/bin/env python
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

import simpy
from log import Log
from singleton import Singleton
from node import Node
from event import Event
from events import Events

@Singleton
class sim:
    """sim.
        Simulation class for a bgp experiment
    """

    
    def __init__(self):
        """__init__
            Init of the simulation class
        """
        self._env = simpy.Environment()

    def config(self, outFile):
        """config.
            Configuration function for the current simulation
            FUTURE:
            - pass a file with the conf environment
        :param outFile: output for the logger
        """
        self._outfile = outFile

    def initialize(self):
        """initialize."""
        self._logger = Log(self._outfile, log_states = True)
        self.node1 = Node(1) 
        self.node2 = Node(2)
        self.node1.neighbor = self.node2
        self.node2.neighbor = self.node1
        self._env.run(until=60)

    @property
    def env(self):
        """env."""
        return self._env

    @env.deleter
    def env(self):
        """env."""
        del self._env
    
    @property
    def logger(self):
        """logger."""
        return self._logger

    @logger.deleter
    def logger(self):
        """logger."""
        del self._logger
