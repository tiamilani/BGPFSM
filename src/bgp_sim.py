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

import sys
sys.path.insert(1, 'util')

import simpy
import time
import random
import networkx as nx
from config import Config
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

    # name of the section in the configuration file that includes all simulation
    # parameters
    PAR_SECTION = "Simulation"
    # simulation duration parameter
    PAR_DURATION = "duration"
    # seed for PRNGs
    PAR_SEED = "seed"
    # Graph file
    PAR_GRAPH = "graph"
    # Verbose param
    PAR_VERBOSE = "verbose"

    def __init__(self):
        """__init__
            Init of the simulation class
        """
        self._env = simpy.Environment()
        self.nodes = {}
        self._configFile = ""
        self._section = ""
        self.verbose = False

    def set_config(self, config_file, section):
        """config.
            Configuration function for the current simulation
            FUTURE:
            - pass a file with the conf environment
        :param outFile: output for the logger
        """
        self._configFile = config_file 
        self._section = section
        self._config = Config(self._configFile, self._section)

    def get_runs_count(self):
        """
        Returns the number of runs for the fiven config file and section
        :returns: the total number of runs
        """
        if self._configFile == "" or self._section == "":
            print("Configuration error. Call set_config() before "
                    "get_runs_count()")
            sys.exit(1)
        return self._config.get_runs_count()

    def get_params(self, run_number):
        """
        Returns a textual representation of simulation parameters for a given
        run number
        :param run_number: the run number
        :returns: textual representation of parameters for run_number
        """
        return self._config.get_params(run_number)

    def initialize(self, run):
        """initialize.
        :param run: the index of the simulation to be run
        """

        if self._configFile == "" or self._section == "":
            print("Configuration error. Call set_config() before initialize()")
            sys.exit(1)

        # set and check run number
        self.run_number = run
        if self.run_number >= self._config.get_runs_count():
            print("Simulation error. Run number %d does not exist. Please run "
                "the simulator with the --list option to list all possible "
                "runs" % run_number)
            sys.exit(1)

        self._config.set_run_number(self.run_number)
        self._logger = Log(self._config.get_output_file(), log_states = True)
        # Get simulation duration
        self.duration = self._config.get_param(self.PAR_DURATION)
        # Get seeds, each seed generates a simulation repetition
        self.seed = self._config.get_param(self.PAR_SEED)
        random.seed(self.seed)
        if self._config.get_param(self.PAR_VERBOSE) is not None:
            self.verbose = self._config.get_param(self.PAR_VERBOSE) in ("True", "true")

        self.graphFile = self._config.get_param(self.PAR_GRAPH)
        self.G = nx.read_graphml(self.graphFile)
        for v in self.G.nodes(data=True):
            node = Node(v[0])
            self.nodes[node.id] = node

        for e in self.G.edges(data=True):
            self.nodes[e[0]].add_neighbor(self.nodes[e[1]])
        self._initialize = True

    def run(self):
        # Check if the system has been initialized
        if not self.initialize:
            print("Cannot run the simulation. Call initialize() first")
            sys.exit(1)

        start_time = time.time()
        # Execute the simulation
        self._env.run(until=self.duration)
        end_time = time.time()
        total_time = round(end_time - start_time)
        print("\nMaximum simulation time reached. Terminating")
        print("Total simulation time: %d hours, %d minutes, %d seconds" %
                (total_time // 3600, total_time % 3600 // 60,
                total_time % 3600 % 60))

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
