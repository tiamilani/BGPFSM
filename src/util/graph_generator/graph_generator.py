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
parser.add_argument("-t", "--type", dest="type", default="elmokashfi",
                  action="store", help="define the type of network to generate")
parser.add_argument("-o", "--outpute", dest="out", default="graph.graphml",
                  action="store", help="define the output graph")
parser.add_argument("-n", "--nodes", dest="nodes", default=1000, action="store",
                  help="defines the number of nodes to generate", type=int)
parser.add_argument("-mt", "--mraitype", dest="mrai_strategy", default="constant",
                  action="store", help="define the type of mrai to apply")
parser.add_argument("-m", "--mrai", dest="default_mrai", default=0.0, action="store",
                  help="defines the default mrai that will be applyed", type=float)
parser.add_argument("-p", "--policies", dest="policies", default="True",
                    action="store_false", help="remove the introduction of policies \
                    on the links")
parser.add_argument("-s", "--seed", dest="seed", default=1234, action="store",
                  help="defines the seed used during the generation", type=int)

graph_strategies = []
mrai_strategies = []

def graph_strategy(func):
    """ Wrapper for strategy definition; it adds strategy name to the strategy list.
    Strategy name *must not* include an underscore and the function *must* be
    called "apply_<strategyname>_strategy".
    """
    graph_strategies.append(func.__qualname__.split('_')[1])
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def graph_strategyfy(strategy:str, number_of_nodes: int, seed: int = 1234) -> nx.DiGraph:
    if strategy in graph_strategies:
        return eval("apply_" + strategy + "_strategy")(number_of_nodes, seed)
    else:
        raise ValueError(f"Strategy \"{strategy}\" not available")

def mrai_strategy(func):
    """ Wrapper for strategy definition; it adds strategy name to the strategy list.
    Strategy name *must not* include an underscore and the function *must* be
    called "apply_<strategyname>_strategy".
    """
    mrai_strategies.append(func.__qualname__.split('_')[1])
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def mrai_strategyfy(strategy:str, G: nx.DiGraph, value: float) -> nx.DiGraph:
    if strategy in mrai_strategies:
        eval("apply_" + strategy + "_strategy")(G, value)
    else:
        raise ValueError(f"Strategy \"{strategy}\" not available")

def correct_graph_data(G: nx.DiGraph) -> None:
    for node in G.nodes(data=True):
        del G.nodes[node[0]]['type']
        if 'peers' in G.nodes[node[0]]:
            del G.nodes[node[0]]['peers']
    for edge in G.edges(data=True):
        if G.edges[(edge[0], edge[1])]['type'] == "peer":
            G.edges[(edge[0], edge[1])]['policy'] = "1, inf, inf"
        elif G.edges[(edge[0], edge[1])]['type'] == "transit":
            if G.edges[(edge[0], edge[1])]['customer'] == edge[0]:
                G.edges[(edge[0], edge[1])]['policy'] = "0, inf, inf"
            else:
                G.edges[(edge[0], edge[1])]['policy'] = "2, 2, 2"
        del G.edges[(edge[0], edge[1])]['type']
        del G.edges[(edge[0], edge[1])]['customer']

def insert_random_destination(G: nx.DiGraph) -> None:
    types = nx.get_node_attributes(G, "type")
    reverse_types = defaultdict(list)
    {reverse_types[v].append(k) for k, v in types.items()}
    node = random.choice(reverse_types['C'])
    G.nodes[node]['destinations'] = "100.0.0.0/24"

@graph_strategy
def apply_elmokashfi_strategy(number_of_nodes: int, seed: int = 1234) -> nx.DiGraph:
    G = nx.random_internet_as_graph(number_of_nodes, seed)
    G = nx.DiGraph(G)
    insert_random_destination(G)
    correct_graph_data(G)
    return G

@mrai_strategy
def apply_constant_strategy(G :nx.DiGraph, value: float) -> None:
    nx.set_edge_attributes(G, value, "mrai")

def main():
    options = parser.parse_args()
    
    G = graph_strategyfy(options.type, options.nodes, options.seed)
    mrai_strategyfy(options.mrai_strategy, G, options.default_mrai)
    nx.write_graphml(G, options.out)

if __name__ == "__main__":
    main()
