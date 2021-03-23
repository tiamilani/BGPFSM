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
MAIN module
===========

Use this module to control the entire experimentation toolchain

"""

from __future__ import print_function, unicode_literals

import sys
import os

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


def graph_configuration():
    """graph_configuration.
    Procedure to create the graph configuration
    """
    # Ask to the user to load a graph
    ans_graph_load = prompt(qs.graph_load)
    # Look forward for the asware from the user
    if ans_graph_load[s.load_graph_name]:
        graphml_loader = qs.generic_file_load
        graphml_loader[0]['validate'] = qs.graphml_validator
        graph_file = prompt(graphml_loader)
        print(graph_file)
    pprint("Create new graph")
    return None


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
    graph_conf = graph_configuration()
    return ans_load


def main():
    title = Figlet(font="slant")
    print(title.renderText("BGP Sim"))

    # Load the configuration
    conf = configuration()

    pprint(conf)


if __name__ == "__main__":
    main()
