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
# Copyright (C) 2021 Mattia Milani <mattia.milani@studenti.unitn.it>

"""
Strings module
==============

This module is used to keep all the strings used in the program
in a single file.

"""

NAME = "BGP sim"
test = "Test"

# Generic errors
number_lower_error = "The number must be higher"
not_a_number_error = "Please insert a valid number"

# Generic file load
generic_file_load_name = "gneric_file_load"
generic_file_load_message = "Insert the path to the file:"
generic_file_load_invalid_message = "Invalid file"

# Generic folder load
generic_folder_name = "generic_folder_load"
generic_folder_message = "Insert the path to the folder:"
invalid_folder = "Invalid folder, please insert the path to a valid folder"

# Question messages
load_component_name = "load_conf"
load_conf = "Would you like to load a configuration? otherwise you will have to \
create a new one"

# Graph loading
load_graph_name = "load_graph"
load_graph_message = "Would you like to use an already existing graph? "
invalid_graphml_file = "Invalid file, please use a valid graphml file"
# Graph creation
graph_name_name = "graph_name"
graph_name_message = "Define a name for the graph:"
graph_type_list_name = "graph_type"
graph_type_list_message = "Select one graph type"
graph_type_list = ["elmokashfi", "clique"]
graph_nodes_number_name = "graph_nodes"
graph_nodes_number_message = "Define the number of nodes required:"
graph_policies_name = "graph_policies"
graph_policies_message = "Would you like to introduce policies? [def: Y]"
graph_seed_name = "graph_seed"
graph_seed_message = "Define the RNG seed (not necessary for cliques)? [def: 1234]"
error_graph_file_already_exists = "The graph file already exists, please use a \
different name or use a different path"
# Graph centrality
use_graph_centrality_name = "use_graph_centrality"
use_graph_centrality_message = "Would you like to introduce centrality metrics \
in your graph? [def: Y]"
graph_centrality_name = "graph_centrality_type"
graph_centrality_message = "Which centrality metric do you want to use?"
graph_centrality_list = ["betweenness", "dpc"]
# Graph destination
graph_destination_number_name = "graph_destination"
graph_destination_number_message = "Define the number of destinations required:"
graph_dst_strategy_name = "graph_dst_type"
graph_dst_strategy_message = "Which destination strategy do you want to use?"
graph_dst_strategy_list = ["random", "hierarchical"]
graph_dst_seed_name = "graph_dst_seed"
graph_dst_seed_message = "Define the RNG seed for the node selection? [def: 1234]"
graph_dst_hier_name = "graph_hier_level"
graph_dst_hier_message = "Select the hierarchical level where the node should \
be selected [default: 1]"
# Graph MRAI
use_graph_MRAI_name = "use_graph_MRAI"
use_graph_MRAI_message = "Would you like to introduce MRAI attributes on the \
graph? [def: Y]"
graph_MRAI_strategy_name = "graph_MRAI_type"
graph_MRAI_strategy_message = "Which MRAI strategy do you want to use?"
graph_MRAI_strategies_list = ['constant', 'random', 'dpc_noNorm', 'dpc',
                              'reverse_dpc', 'centrality', 'banded_centrality',
                              'reverse_centrality', 'reverse_banded_centrality']
graph_MRAI_value_name = "graph_MRAI_value"
graph_MRAI_value_message = "Define the MRAI value that should be used"
graph_MRAI_seed_name = "graph_MRAI_seed"
graph_MRAI_seed_message = "Define the seed that should be used to set MRAI \
[def: 1234]"
graph_MRAI_mean_name = "graph_MRAI_mean"
graph_MRAI_mean_message = "Define the MRAI mean value that MUST be respected \
by the network, use a negative value to avoid it [def: -1]"
# Graph RFD
use_graph_RFD_name = "use_graph_RFD"
use_graph_RFD_message = "Would you like to introduce RFD attributes on the \
graph? [def: Y]"
graph_RFD_strategy_name = "graph_RFD_type"
graph_RFD_strategy_message = "Which RFD strategy do you want to use?"
graph_RFD_strategies_list = ['cisco', 'juniper', 'cisco7196aggressive',
                             'juniper7196aggressive', 'cisco7196conservative',
                             'juniper7196conservative']
