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
import simpy
import time
import random
import networkx as nx

sys.path.insert(1, 'util')
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
    # Destnations param
    PAR_NETWORK = "destinations"

    def __init__(self):
        """__init__
            Init of the simulation class
        """
        # Loacl variables initialization
        self._env = simpy.Environment()
        self.nodes = {}
        self._configFile = ""
        self._section = ""
        self.verbose = False
        self._initialize = False
        self._config = None
        self._logger = None
        self.duration = 0
        self.seed = 0


    def set_config(self, config_file, section):
        """config.
            Configuration function for the current simulation
        :param config_file: file that contains the configuration
        :param section: section of the file that have to be considered
        """
        self._configFile = config_file
        self._section = section
        # Save the configuration object
        self._config = Config(self._configFile, self._section)

    def get_runs_count(self):
        """
        Returns the number of runs for the fiven config file and section
        :returns: the total number of runs
        """

        # Check if the configuration has been done
        if self._configFile == "" or self._section == "":
            print("Configuration error. Call set_config() before "
                  "get_runs_count()")
            sys.exit(1)
        # Return the set of runs
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

        # Check if the configuration has been setted
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

        # Set run number
        self._config.set_run_number(self.run_number)
        # Set the logger
        self._logger = Log(self._config.get_output_file(), log_states=True)
        # Get simulation duration
        self.duration = self._config.get_param(self.PAR_DURATION)
        # Get seeds, each seed generates a simulation repetition
        self.seed = self._config.get_param(self.PAR_SEED)
        random.seed(self.seed)
        # Check the verbose param
        if self._config.get_param(self.PAR_VERBOSE) is not None:
            self.verbose = self._config.get_param(self.PAR_VERBOSE) in ("True", "true")

        # Setup the graph and nodes
        graphFile = self._config.get_param(self.PAR_GRAPH)
        G = nx.read_graphml(graphFile)
        for v in G.nodes(data=True):
            node = Node(v[0], self._config)
            self.nodes[node.id] = node
            if self.PAR_NETWORK in v[1]:
                for net in v[1][self.PAR_NETWORK].split(','):
                    node.add_destination(net, [], None)

        for e in G.edges(data=True):
            self.nodes[e[0]].add_neighbor(self.nodes[e[1]])

        # Mark the initialization as done
        self._initialize = True

    def run(self):
        # Check if the system has been initialized
        if not self.initialize:
            print("Cannot run the simulation. Call initialize() first")
            sys.exit(1)

        # Register the start time
        start_time = time.time()
        # Execute the simulation
        self._env.run(until=self.duration)
        # Register the end time and do the subtraction
        end_time = time.time()
        total_time = round(end_time - start_time)
        for node in self.nodes:
            print(self.nodes[node])
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
