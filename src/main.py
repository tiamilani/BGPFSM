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
MAIN module
===========

Use this module to control the entire experimentation toolchain

"""

from __future__ import print_function, unicode_literals

import sys
import os
import subprocess

from pyfiglet import Figlet
from PyInquirer import style_from_dict, Token, prompt
from pprint import pprint

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/util/')
import questions as qs
import strings as s

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})


GRAPH_GENERATOR = "util/graph_generator/graph_generator.py"
GRAPH_CENTRALITY_INTRO = "util/graph_generator/insert_centrality.py"
GRAPH_DESTINATION_INTRO = "util/graph_generator/insert_destination.py"
GRAPH_MRAI_INTRO = "util/graph_generator/mrai_setter.py"
GRAPH_RFD_INTRO = "util/graph_generator/rfd_setter.py"
ENVIRONMENT_TEMPLATE_FILE = "templates/environment.template"
EXP_SINGLE = "fsm.py"


def execute_command(command: list):
    """execute_command.
    Execute a command directly on the shell

    Parameters
    ----------
    command : list
        command to execute
    """
    subprocess.run(command)
    return None


def execute_gen_graph(graph_dict: dict):
    """execute_gen_graph.
    Execute the generation of the graph starting from the dictionary that
    represents it.

    Parameters
    ----------
    graph_dict : dict
        graph_dict
    """
    command = ["python3", GRAPH_GENERATOR]
    # Include the graph type
    command.append("-t")
    command.append(graph_dict[s.graph_type_list_name])
    # Include the output
    command.append("-o")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    # Include the number of nodes
    command.append("-n")
    command.append(graph_dict[s.graph_nodes_number_name])
    # Include policy generation or denay it
    if not graph_dict[s.graph_policies_name]:
        command.append("-p")
    # Include the seed
    command.append("-s")
    command.append(graph_dict[s.graph_seed_name])
    execute_command(command)
    return None


def execute_graph_centrality_intro(graph_dict: dict) -> None:
    """execute_graph_centrality_intro.
    Instruction of the centrality metric required on the graph

    Parameters
    ----------
    graph_dict : dict
        graph_dict used to obtain the position of the graph
    """
    command = ["python3", GRAPH_CENTRALITY_INTRO]
    # Include type
    command.append("-t")
    command.append(graph_dict[s.graph_centrality_name])
    # Include original graph
    command.append("-f")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name].split('.')[0] +
                   "_original.graphml")
    # Include the output graph
    command.append("-o")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    execute_command(command)
    return None


def execute_graph_destination_intro(graph_dict: dict) -> None:
    command = ["python3", GRAPH_DESTINATION_INTRO]
    # Include type
    command.append("-t")
    command.append(graph_dict[s.graph_dst_strategy_name])
    # Include number of networks
    command.append("-n")
    command.append(graph_dict[s.graph_destination_number_name])
    # Include input file
    command.append("-f")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    # Include output file
    command.append("-o")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    # Include the seed
    command.append("-s")
    command.append(graph_dict[s.graph_dst_seed_name])
    if graph_dict[s.graph_dst_hier_name] is not None:
        # Include hierarchical level
        command.append("-H")
        command.append(graph_dict[s.graph_dst_hier_name])
    execute_command(command)
    return None


def execute_graph_mrai_intro(graph_dict: dict) -> None:
    command = ["python3", GRAPH_MRAI_INTRO]
    # Include type
    command.append("-t")
    command.append(graph_dict[s.graph_MRAI_strategy_name])
    # Include input file
    command.append("-f")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    # Include output file
    command.append("-o")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    # Include the seed
    command.append("-s")
    command.append(graph_dict[s.graph_MRAI_seed_name])
    # Include the MRAI value required
    command.append("-m")
    command.append(graph_dict[s.graph_MRAI_value_name])
    # Include the mean MRAI required
    command.append("-M")
    command.append(graph_dict[s.graph_MRAI_mean_name])
    execute_command(command)
    return None


def execute_graph_rfd_intro(graph_dict: dict) -> None:
    command = ["python3", GRAPH_RFD_INTRO]
    # Include type
    command.append("-t")
    command.append(graph_dict[s.graph_RFD_strategy_name])
    # Include input file
    command.append("-f")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    # Include output file
    command.append("-o")
    command.append(graph_dict[s.generic_folder_name] + "/" +
                   graph_dict[s.graph_name_name])
    execute_command(command)
    return None

def execute_single_experiment(env_file: str, exp_dict: dict) -> None:
    command = ["python3", EXP_SINGLE]
    # Include the environment file
    command.append("-c")
    command.append(env_file)
    # Include the section to use
    command.append("-s")
    command.append(exp_dict[s.exp_single_run_sim_name])
    # Include the id of the run to execute
    command.append("-r")
    command.append(exp_dict[s.exp_single_run_id_name])
    execute_command(command)
    return None


def graph_creation() -> dict:
    """graph_creation.
    Procedure used to create a graph
    """
    # Define the name of the graph to create
    print("== Graph Creation ==")
    ans_graph_creation = prompt(qs.graph_definition)
    if os.path.isfile(ans_graph_creation[s.generic_folder_name] + "/" +
                      ans_graph_creation[s.graph_name_name]):
        print(s.error_graph_file_already_exists)
        return graph_creation()
    # pprint(ans_graph_creation)
    execute_gen_graph(ans_graph_creation)
    # Attribute introduction
    # Centrality if the graph is an elmokashfi
    if ans_graph_creation[s.graph_type_list_name] == s.graph_type_list[0]:
        ans_use_graph_centrality = prompt(qs.use_graph_centrality)
        ans_graph_creation.update(ans_use_graph_centrality)
        if ans_use_graph_centrality[s.use_graph_centrality_name]:
            ans_graph_centrality = prompt(qs.graph_centrality)
            ans_graph_creation.update(ans_graph_centrality)
            execute_graph_centrality_intro(ans_graph_creation)
    # Destinations
    ans_graph_destination = prompt(qs.graph_destination_intro)
    ans_graph_Hdst = {s.graph_dst_hier_name: None}
    if ans_graph_destination[s.graph_dst_strategy_name] == s.graph_dst_strategy_list[1]:
        ans_graph_Hdst = prompt(qs.use_hier_dst)
    ans_graph_destination.update(ans_graph_Hdst)
    ans_graph_creation.update(ans_graph_destination)
    execute_graph_destination_intro(ans_graph_creation)
    # MRAI
    # Check if MRAI is required
    ans_graph_creation.update(prompt(qs.use_MRAI))
    if ans_graph_creation[s.use_graph_MRAI_name]:
        # Get MRAI values to use
        ans_graph_creation.update(prompt(qs.graph_MRAI_intro))
    execute_graph_mrai_intro(ans_graph_creation)
    # RFD
    # Check if RFD is required
    ans_graph_creation.update(prompt(qs.use_RFD))
    if ans_graph_creation[s.use_graph_RFD_name]:
        # Get RFD values to use
        ans_graph_creation.update(prompt(qs.graph_RFD_intro))
    execute_graph_rfd_intro(ans_graph_creation)
    return ans_graph_creation


def graph_configuration():
    """graph_configuration.
    Procedure to create the graph configuration
    """
    # Ask to the user to load a graph
    graph_creation = None
    file = None
    ans_graph_load = prompt(qs.graph_load)
    # Look forward for the asware from the user
    if ans_graph_load[s.load_graph_name]:
        graphml_loader = qs.generic_file_load
        graphml_loader[0]['validate'] = qs.graphml_validator
        file = prompt(graphml_loader)[s.generic_file_load_name]
    else:
        graph_creation = graph_creation()
        file = graph_creation[s.generic_folder_name] + "/" + \
               graph_creation[s.graph_name_name]
    return file, graph_creation


def environment_creation() -> dict:
    print('== Environment Creation ==')
    ans_env_creation = prompt(qs.environment_definition)
    if os.path.isfile(ans_env_creation[s.generic_folder_name] + "/" +
                      ans_env_creation[s.env_file_name]):
        print(s.error_env_file_already_exists)
        return environment_creation()
    print("It is not possible to configure the distributions through this "+\
          "tool, please consider modify them manually opening the file " + \
           ans_env_creation[s.generic_folder_name] + "/" + \
           ans_env_creation[s.env_file_name] + ", thanks for your " +
          "chomprension.")
    return ans_env_creation


def environment_configuration(graph_file: str = s.environment_default_graph):
    envinronment_variables = {
            s.environment_tag_name: s.environment_default_name,
            s.environment_tag_seed: s.environment_default_seed,
            s.environment_tag_duration: s.environment_default_duration,
            s.environment_tag_graph: graph_file,
            s.environment_tag_output: s.environment_default_output,
            s.environment_tag_verbose: s.environment_default_verbose,
            s.environment_tag_s_flag: s.environment_default_s_flag,
            s.environment_tag_s_sequence: s.environment_default_s_sequence,
            s.environment_tag_iw_flag: s.environment_default_iw_flag,
            s.environment_tag_w_flag: s.environment_default_w_flag,
            s.environment_tag_r_flag: s.environment_default_r_flag,
            s.environment_tag_w_dist: s.environment_default_w_dist,
            s.environment_tag_r_dist: s.environment_default_r_dist,
            s.environment_tag_d_dist: s.environment_default_d_dist,
            s.environment_tag_p_dist: s.environment_default_p_dist,
            s.environment_tag_del_dist: s.environment_default_del_dist
        }
    # Variables
    output_file = None
    env_creation = None
    # Ask to load an env file
    ans_env_load = prompt(qs.environment_load)
    if ans_env_load[s.load_env_name]:
        environment_loader = qs.generic_file_load
        environment_loader[0]['validate'] = qs.json_validator
        output_file = prompt(environment_loader)[s.generic_file_load_name]
    else:
        # Create a new configuration for the environment
        env_creation = environment_creation()
        envinronment_variables.update(env_creation)
        # Write the template into the output file
        with open(ENVIRONMENT_TEMPLATE_FILE, "r") as env_template:
            environment_template = env_template.read()

        output_file = envinronment_variables[s.generic_folder_name] + "/" + \
                      envinronment_variables[s.env_file_name]
        file = open(output_file, "w+")
        file.write(environment_template.format(**envinronment_variables))
    return output_file, env_creation


def execute_experiments(env_file: str, exp_dict: dict) -> None:
    if exp_dict[s.exp_type_name] == s.exp_single_run:
        execute_single_experiment(env_file, exp_dict)


def experiments_configuration(env_file: str) -> dict:
    experiments_conf = None
    experiments_conf = prompt(qs.experiments)
    execute_experiments(env_file, experiments_conf)
    return experiments_conf


def configuration():
    """configuration.
    procedure to load/create a new configuration for the experiments
    """
    # Ask to the user to load a configuration
    ans_load = prompt(qs.loading_questions)
    if ans_load[s.load_component_name]:
        # Load the configuration and return it
        return None
    # Create a new configuration
    graph_file, graph_conf = graph_configuration()
    env_file, env_conf = environment_configuration(graph_file)
    print("== The environment is compleatly configured now is possible to execute experiments==")
    experiments_conf = experiments_configuration(env_file)
    print("== Experiments concluded, now is possible to analyze the output ==")
    # analysis_conf = experiments_configuration(env_conf)
    return ans_load


def main():
    title = Figlet(font="slant")
    print(title.renderText("BGP Sim"))

    # Load the configuration
    conf = configuration()

    pprint(conf)


if __name__ == "__main__":
    main()
