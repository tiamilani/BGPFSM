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
Insert destination module
======================

Module used to insert a destination in a graph 
"""

import networkx as nx
import argparse
import functools
from collections import defaultdict
import random
import matplotlib.pyplot as plt
import ipaddress

import milaniBGPLoad as DPC

parser = argparse.ArgumentParser(usage="usage: graph_generator [options]",
                      description="Generate different possible graphs",
                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--type", dest="type", default="elmokashfi",
                  action="store", help="define the type of network to generate")
parser.add_argument("-n", "--networks", dest="networks", default=100, action="store",
                  help="defines the number of networks to generate", type=int)
parser.add_argument("-f", "--file", dest="input", default="graph.graphml",
                  action="store", help="define the input graph")
parser.add_argument("-o", "--output", dest="out", default="graph.graphml",
                  action="store", help="define the output graph")
parser.add_argument("-s", "--seed", dest="seed", default=1234, action="store",
                  help="defines the seed used during the generation", type=int)

destination_strategies = []

def destination_strategy(func):
    """ Wrapper for strategy definition; it adds strategy name to the strategy list.
    Strategy name *must not* include an underscore and the function *must* be
    called "apply_<strategyname>_strategy".
    """
    destination_strategies.append(func.__qualname__.split('_')[1])
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def destination_strategyfy(strategy:str, graph: nx.DiGraph, destination: ipaddress.IPv4Network, seed: int = 1234, types: list = ["C"]) -> nx.DiGraph:
    if strategy in destination_strategies:
        eval("apply_" + strategy + "_strategy")(graph, destination, seed, types)
    else:
        raise ValueError(f"Strategy \"{strategy}\" not available")

@destination_strategy
def apply_random_strategy(G: nx.DiGraph, destination: ipaddress.IPv4Network, seed: int = 1234, t: list = ["C"]) -> None:
    types = nx.get_node_attributes(G, "type")
    reverse_types = defaultdict(list)
    {reverse_types[v].append(k) for k, v in types.items()}
    random.seed(seed)
    inserted = False
    while (not inserted):
        items = []
        for elem in t:
            items += reverse_types[elem]
        node = random.choice(items)
        if 'destinations' not in G.nodes[node]:
            G.nodes[node]['destinations'] = str(destination)
            inserted = True

def main():
    options = parser.parse_args()
    
    random.seed(options.seed)
    out_name = options.out.rsplit('.', 1)[0]
    G = nx.read_graphml(options.input)
    node_networks = list(ipaddress.ip_network(u'100.0.0.0/8').subnets(new_prefix=24))
    for i in range(options.networks):
        destination = node_networks[i]
        destination_strategyfy(options.type, G, destination, options.seed, ["C"])

    nx.write_graphml(G, out_name + ".graphml")

if __name__ == "__main__":
    main()
