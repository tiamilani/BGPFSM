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
not_a_number_list_error = "Please insert a valid list of numbers exp: '1 2 3'"

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

# environment template
environment_tag_name = "env_name"
environment_tag_seed = "seed_array"
environment_tag_duration = "duration"
environment_tag_graph = "graph_file"
environment_tag_output = "output_file"
environment_tag_verbose = "verbose_flag"
environment_tag_s_flag = "signaling_flag"
environment_tag_s_sequence = "signaling_sequence"
environment_tag_iw_flag = "implicit_withdraw_flag"
environment_tag_w_flag = "withdraw_flag"
environment_tag_r_flag = "reannouncement_flag"
environment_tag_w_dist = "withdraw_distribution"
environment_tag_r_dist = "reannouncement_distribution"
environment_tag_d_dist = "datarate_distribution"
environment_tag_p_dist = "processing_distribution"
environment_tag_del_dist = "delay_distribution"

environment_default_name = "simulation"
environment_default_seed = "[0, 1, 2]"
environment_default_duration = "600"
environment_default_graph = "not_existing_graph.graphml"
environment_default_output = "results/default/{date-time}/output_{seed}.csv"
environment_default_verbose = "True"
environment_default_s_flag = "True"
environment_default_s_sequence = "AWAWA"
environment_default_iw_flag = "True"
environment_default_w_flag = "True"
environment_default_r_flag = "False"
environment_default_w_dist = """{\"distribution\": \"const\", \"mean\": 300}"""
environment_default_r_dist = """{\"distribution\": \"const\", \"mean\": 300}"""
environment_default_d_dist = """{\"distribution\": \"exp\", \"lambda\" : 100}"""
environment_default_p_dist = """{\"distribution\": \"const\", \"mean\": 0.00001}"""
environment_default_del_dist = """{\"distribution\": \"unif\", \"min\": 0.012, \"max\": 3, \"int\": 0.001}"""

# Environment errors
invalid_signal_sequence = "Please insert a valid signal sequence, like 'AWAW'"
error_env_file_already_exists = "The JSON file already exists, please use a \
different name or use a different path"

# Environment loading
load_env_name = "environment_load"
load_env_message = "Would you like to load an environment file? Otherwise you \
will have to create a new one [def: Y]"
invalid_json_file = "Invalid file, please use a valid JSON file"

# Environment configuration
env_file_name = "env_file"
env_file_message = "Insert the name of the json environment file to create:"
env_name_message = "Please define a name for the environment you would like \
to create [def:" + environment_default_name + "]:"
env_seeds_message = "Please define the list of seeds that should be used by \
the environment [exp: 1 2 3]:"
env_duration_message = "Please define a max duration for your environment:"
env_output_message = "Please define the output format for your experiments \
[def: " + environment_default_output + "]:"
env_signal_flag_message = "Would you like to use signals? [def: Y]"
env_signal_message = "Define the signal you would like to use [def: " + \
environment_default_s_sequence + "]:"
env_iw_flag_message = "Would you like to activate IW? [def: Y]"
env_w_flag_message = "Would you like to activate the withdraw propery? [def: Y]"
env_r_flag_message = "Would you like to activate the retransmission propery? [def: Y]"

# Experiments
exp_type_name = "exp_type"
exp_type_message = "Select which type of experiments you want to run:"
# single experiment
exp_single_run = "Single run"
exp_single_run_id_name = "single_run_id"
exp_single_run_id_message = "Define the id of the run that you want to execute:"
exp_single_run_sim_name = "single_run_sim"
exp_single_run_sim_message = "Define the name of the environment you would like to use:"

# Exp list
exp_type_list = [exp_single_run]
