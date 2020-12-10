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

"""
Graph generator module
======================

Module used to generate different graphs
"""

import networkx as nx
import argparse
import functools
from collections import defaultdict
import random


parser = argparse.ArgumentParser(usage="usage: %prog [options]",
                      description="Generate different possible graphs",
                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--type", dest="type", default="None",
                  choices=['cisco', 'juniper', 'cisco7196aggressive',
                      'juniper7196aggressive', 'cisco7196conservative',
                      'juniper7196conservative'],
                  action="store", help="define the type of rfd to apply")
parser.add_argument("-f", "--file", dest="inputFile", default="graph.graphml",
                  action="store", help="define the input graph")
parser.add_argument("-o", "--output", dest="out", default="graph.graphml",
                  action="store", help="define the output graph")

CISCO_W_PENALTY = 1.0
CISCO_RA_PENALTY = 0.0
CISCO_AC_PENALTY = 0.5
CISCO_CUT = 2.0
CISCO_REUSE = 0.75
CISCO_T_HOLD = 3600
CISCO_DECAY_OK = 900
CISCO_DECAY_NG = 900
CISCO_DECAY_MEMORY_LIMIT_OK = 3600
CISCO_DECAY_MEMORY_LIMIT_NG = 3600
CISCO_DELTA_T = 5
CISCO_CONF = [CISCO_W_PENALTY, CISCO_RA_PENALTY, CISCO_AC_PENALTY,
              CISCO_CUT, CISCO_REUSE, CISCO_T_HOLD, CISCO_DECAY_OK,
              CISCO_DECAY_NG, CISCO_DECAY_MEMORY_LIMIT_OK, CISCO_DECAY_MEMORY_LIMIT_NG,
              CISCO_DELTA_T]

CISCO_7196_AGGRESSIVE_CUT = 6.0
CISCO_7196_AGGRESSIVE = [CISCO_W_PENALTY, CISCO_RA_PENALTY, CISCO_AC_PENALTY,
              CISCO_7196_AGGRESSIVE_CUT, CISCO_REUSE, CISCO_T_HOLD, CISCO_DECAY_OK,
              CISCO_DECAY_NG, CISCO_DECAY_MEMORY_LIMIT_OK, CISCO_DECAY_MEMORY_LIMIT_NG,
              CISCO_DELTA_T]

CISCO_7196_CONSERVATIVE_CUT = 12.0
CISCO_7196_CONSERVATIVE = [CISCO_W_PENALTY, CISCO_RA_PENALTY, CISCO_AC_PENALTY,
              CISCO_7196_CONSERVATIVE_CUT, CISCO_REUSE, CISCO_T_HOLD, CISCO_DECAY_OK,
              CISCO_DECAY_NG, CISCO_DECAY_MEMORY_LIMIT_OK, CISCO_DECAY_MEMORY_LIMIT_NG,
              CISCO_DELTA_T]

JUNIPER_W_PENALTY = 1.0
JUNIPER_RA_PENALTY = 1.0
JUNIPER_AC_PENALTY = 0.5
JUNIPER_CUT = 3.0
JUNIPER_REUSE = 0.75
JUNIPER_T_HOLD = 3600
JUNIPER_DECAY_OK = 900
JUNIPER_DECAY_NG = 900
JUNIPER_DECAY_MEMORY_LIMIT_OK = 3600
JUNIPER_DECAY_MEMORY_LIMIT_NG = 3600
JUNIPER_DELTA_T = 5
JUNIPER_CONF = [JUNIPER_W_PENALTY, JUNIPER_RA_PENALTY, JUNIPER_AC_PENALTY,
              JUNIPER_CUT, JUNIPER_REUSE, JUNIPER_T_HOLD, JUNIPER_DECAY_OK,
              JUNIPER_DECAY_NG, JUNIPER_DECAY_MEMORY_LIMIT_OK, JUNIPER_DECAY_MEMORY_LIMIT_NG,
              JUNIPER_DELTA_T]

JUNIPER_7196_AGGRESSIVE_CUT = 6.0
JUNIPER_7196_AGGRESSIVE = [JUNIPER_W_PENALTY, JUNIPER_RA_PENALTY, JUNIPER_AC_PENALTY,
              JUNIPER_7196_AGGRESSIVE_CUT, JUNIPER_REUSE, JUNIPER_T_HOLD, JUNIPER_DECAY_OK,
              JUNIPER_DECAY_NG, JUNIPER_DECAY_MEMORY_LIMIT_OK, JUNIPER_DECAY_MEMORY_LIMIT_NG,
              JUNIPER_DELTA_T]

JUNIPER_7196_CONSERVATIVE_CUT = 12.0
JUNIPER_7196_CONSERVATIVE = [JUNIPER_W_PENALTY, JUNIPER_RA_PENALTY, JUNIPER_AC_PENALTY,
              JUNIPER_7196_CONSERVATIVE_CUT, JUNIPER_REUSE, JUNIPER_T_HOLD, JUNIPER_DECAY_OK,
              JUNIPER_DECAY_NG, JUNIPER_DECAY_MEMORY_LIMIT_OK, JUNIPER_DECAY_MEMORY_LIMIT_NG,
              JUNIPER_DELTA_T]


rfd_strategies = []

def rfd_strategy(func):
    """ Wrapper for strategy definition; it adds strategy name to the strategy list.
    Strategy name *must not* include an underscore and the function *must* be
    called "apply_<strategyname>_strategy".
    """
    rfd_strategies.append(func.__qualname__.rsplit('_', 1)[0].split('_', 1)[1])
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def rfd_strategyfy(strategy:str, G: nx.DiGraph) -> nx.DiGraph:
    if strategy in rfd_strategies:
        eval("apply_" + strategy + "_strategy")(G)
    else:
        raise ValueError(f"Strategy \"{strategy}\" not available in {rfd_strategies}")

@rfd_strategy
def apply_cisco_strategy(G: nx.DiGraph) -> None:
    conf = str(CISCO_CONF).replace('[', '').replace(']', '')
    nx.set_node_attributes(G, conf, 'RFD')

@rfd_strategy
def apply_juniper_strategy(G: nx.DiGraph) -> None:
    conf = str(JUNIPER_CONF).replace('[', '').replace(']', '')
    nx.set_node_attributes(G, conf, 'RFD')

@rfd_strategy
def apply_cisco7196aggressive_strategy(G: nx.DiGraph) -> None:
    conf = str(CISCO_7196_AGGRESSIVE).replace('[', '').replace(']', '')
    nx.set_node_attributes(G, conf, 'RFD')

@rfd_strategy
def apply_juniper7196aggressive_strategy(G: nx.DiGraph) -> None:
    conf = str(JUNIPER_7196_AGGRESSIVE).replace('[', '').replace(']', '')
    nx.set_node_attributes(G, conf, 'RFD')

@rfd_strategy
def apply_cisco7196conservative_strategy(G: nx.DiGraph) -> None:
    conf = str(CISCO_7196_CONSERVATIVE).replace('[', '').replace(']', '')
    nx.set_node_attributes(G, conf, 'RFD')

@rfd_strategy
def apply_juniper7196conservative_strategy(G: nx.DiGraph) -> None:
    conf = str(JUNIPER_7196_CONSERVATIVE).replace('[', '').replace(']', '')
    nx.set_node_attributes(G, conf, 'RFD')

def main():
    options = parser.parse_args()

    G = nx.read_graphml(options.inputFile)
    rfd_strategyfy(options.type, G)
    nx.write_graphml(G, options.out)

if __name__ == "__main__":
    main()
