#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the graphNU grapheneral Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# graphNU grapheneral Public License for more details.
#
# You should have received a copy of the graphNU grapheneral Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2020 Mattia Milani <mattia.milani@studenti.unitn.it>

"""
bgp_sim module
==============

Use it to run bgp like simulations

"""

import sys
import time
import random
from pathlib import Path
import os
import simpy
import networkx as nx
import matplotlib.pyplot as plt

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/util/')
from config import Config
from singleton import Singleton
from link import Link
from log import Log
from node import Node
from RFD import RFD_2438


@Singleton
class Sim:
    """sim.
        Simulation class for a bgp experiment
    """

    # name of the section in the configuration file that includes all simulation
    # parameters
    PAR_SECTION = "Simulation"
    # simulation duration parameter
    PAR_DURATION = "duration"
    # seed for PRNgraphs
    PAR_SEED = "seed"
    # graphraph file
    PAR_graphRAPH = "graph"
    # Verbose param
    PAR_VERBOSE = "verbose"
    # Destnations param
    PAR_NETWORK = "destinations"
    # MRAI_affects_withdraws param
    PAR_MRAI_WITHDRAW = "MRAI_affects_withdraws"
    # RFD param
    PAR_RFD = "RFD"
    # ADAPTIVE_RFD
    PAR_ADAPTIVE_RFD = "adaptive_rfd"

    def __init__(self):
        """__init__
            Init of the simulation class
        """

        # Loacl variables initialization
        self._env = simpy.Environment()
        self.nodes = {}
        self._config_file = ""
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
        self._config_file = config_file
        self._section = section
        # Save the configuration object
        self._config = Config(self._config_file, self._section)

    def get_runs_count(self):
        """
        Returns the number of runs for the fiven config file and section
        :returns: the total number of runs
        """

        # Check if the configuration has been done
        if self._config_file == "" or self._section == "":
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
        if self._config_file == "" or self._section == "":
            print("Configuration error. Call set_config() before initialize()")
            sys.exit(1)

        # set and check run number
        run_number = run
        if run_number >= self._config.get_runs_count():
            print("Simulation error. Run number {} does not exist. Please run "
                  "the simulator with the --list option to list all possible "
                  "runs".format(run_number))
            sys.exit(1)

        # Set run number
        self._config.set_run_number(run_number)
        # Set the logger
        Path('/'.join(self._config.get_output_file().split('/')[:-1])).mkdir(
                parents=True, exist_ok=True)
        self._logger = Log(self._config.get_output_file(), log_packets=True,
                            log_paths=True)
        # Get simulation duration
        self.duration = self._config.get_param(self.PAR_DURATION)
        # Get seeds, each seed generates a simulation repetition
        self.seed = self._config.get_param(self.PAR_SEED)
        random.seed(self.seed)
        # Check the verbose param
        if self._config.get_param(self.PAR_VERBOSE) is not None:
            self.verbose = self._config.get_param(self.PAR_VERBOSE) in ("True", "true")

        # Setup the graph and nodes
        graph_file = self._config.get_param(self.PAR_graphRAPH)
        graph = nx.read_graphml(graph_file)
        sharing_nodes = []
        for vert in graph.nodes(data=True):
            node = Node(vert[0], self._config)
            self.nodes[node.id] = node
            if self.PAR_NETWORK in vert[1]:
                for net in vert[1][self.PAR_NETWORK].split(','):
                    node.add_destination(net, [], None)
                sharing_nodes.append(node)
            if self.PAR_MRAI_WITHDRAW in vert[1]:
                if int(vert[1][self.PAR_MRAI_WITHDRAW]) > 0:
                    node.mrai_withdraw = True
            if self.PAR_ADAPTIVE_RFD in vert[1]:
                if int(vert[1][self.PAR_ADAPTIVE_RFD]) > 0:
                    node.adaptive_rfd = True
            if self.PAR_RFD in vert[1]:
                rfd = RFD_2438(vert[1][self.PAR_RFD])
                node.rfd = rfd

        for edge in graph.edges(data=True):
            link_res = simpy.Resource(self._env, capacity=1)
            link = Link(self._env, self.nodes[edge[1]], link_res, edge[2])
            self.nodes[edge[0]].add_neighbor(link)

        for node in sharing_nodes:
            node.force_share_dst()
        # Mark the initialization as done
        self._initialize = True

    def run(self):
        """run.
        Run the simulation with the local configuration
        The simulation must be initialized before running it
        """
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

    def plot_graph(self) -> None:
        """
        plot_grpah
        Used to save a figure of the graph as pdf in the output folder

        :rtype: None
        """
        plt.figure(figsize=(18,14))
        # Get the graph file
        graph_file = self._config.get_param(self.PAR_graphRAPH)
        # Create the networkx graph object
        graph = nx.read_graphml(graph_file)
        # Get a layout
        pos = nx.spring_layout(graph, k=0.7, seed=5)
        # Draw the network
        nx.draw_networkx(graph, pos=pos, arrows=True,
                         with_labels=True,
                         node_size=450, node_color="#ffffff",
                         edgecolors="#000000", font_size=10)
        # Add edge labels
        edge_labels = nx.get_edge_attributes(graph,'policy')
        nx.draw_networkx_edge_labels(graph, pos, edge_labels = edge_labels)
        # Moidfy the output file name
        name = '/'.join(self._config.get_output_file().split('/')[:-1]) + "/graph.pdf"
        # Save only if it is not present
        if not os.path.isfile(name):
            plt.savefig(name)
            plt.close()

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
