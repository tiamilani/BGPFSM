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

import networkx as nx
import argparse
import functools
from collections import defaultdict
import random
import matplotlib.pyplot as plt
import ipaddress

import milaniBGPLoad as DPC

parser = argparse.ArgumentParser(usage="usage: insert_centrality.py [options]",
                      description="Insert centrality from graph1 to graph2",
                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--type", dest="type", default="elmokashfi",
                  action="store", help="define the type of centrality to use")
parser.add_argument("-f", "--file", dest="file", default="original.graphml",
                  action="store", help="Define the input graph file used to calculate \
                                        the centrality value")
parser.add_argument("-o", "--output", dest="out", default="graph.graphml",
                  action="store", help="define the output graph")

centrality_strategies = []

def centrality_strategy(func):
    """ Wrapper for strategy definition; it adds strategy name to the strategy list.
    Strategy name *must not* include an underscore and the function *must* be
    called "apply_<strategyname>_strategy".
    """
    centrality_strategies.append(func.__qualname__.split('_')[1])
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def centrality_strategyfy(strategy:str, input_graph: nx.Graph, output_graph: nx.DiGraph) -> None:
    if strategy in centrality_strategies:
        return eval("apply_" + strategy + "_strategy")(input_graph, output_graph)
    else:
        raise ValueError(f"Strategy \"{strategy}\" not available")

def insert_destinations(graph: nx.Graph) -> None:
    node_networks = list(ipaddress.ip_network(u'100.0.0.0/8').subnets(new_prefix=24))

    i = 0
    for n in graph.nodes(data=True):
        if n[1]['type'] == 'C' or n[1]['type'] == 'CP' or n[1]['type'] == 'M':
            n[1]['destinations'] = str(node_networks[i])
        i += 1

@centrality_strategy
def apply_betweenness_strategy(input_graph: nx.Graph, output_graph: nx.DiGraph) -> None:
    insert_destinations(input_graph)
    cent = nx.betweenness_centrality(input_graph, normalized=False)
    nx.set_node_attributes(output_graph, cent, "centrality")

@centrality_strategy
def apply_dpc_strategy(input_graph: nx.Graph, output_graph: nx.DiGraph) -> None:
    insert_destinations(input_graph)
    cent = DPC.mice_centrality(input_graph, normalized=False)
    nx.set_node_attributes(output_graph, cent, "centrality")

def main():
    options = parser.parse_args()
    
    input_graph = nx.read_graphml(options.file)
    output_graph = nx.read_graphml(options.out)
    centrality_strategyfy(options.type, input_graph, output_graph)
    nx.write_graphml(output_graph, options.out)

if __name__ == "__main__":
    main()
