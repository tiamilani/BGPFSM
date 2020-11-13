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
parser.add_argument("-t", "--type", dest="type", default="random",
                  action="store", help="define the type of network to generate")
parser.add_argument("-f", "--file", dest="inputFile", default="graph.graphml",
                  action="store", help="define the input graph")
parser.add_argument("-o", "--output", dest="out", default="graph.graphml",
                  action="store", help="define the output graph")
parser.add_argument("-m", "--mrai", dest="default_mrai", default=0.0, action="store",
                  help="defines the default mrai that will be applyed", type=float)
parser.add_argument("-s", "--seed", dest="seed", default=1234, action="store",
                  help="defines the seed used during the generation", type=int)
parser.add_argument("-M", "--mean", dest="mean", default=-1, action="store",
                  help="defines the default mean of mrais timers that need to be \
                        respected, with 0.0 the mean should not be evaluated", type=float)

mrai_strategies = []


def mrai_strategy(func):
    """ Wrapper for strategy definition; it adds strategy name to the strategy list.
    Strategy name *must not* include an underscore and the function *must* be
    called "apply_<strategyname>_strategy".
    """
    mrai_strategies.append(func.__qualname__.rsplit('_', 1)[0].split('_', 1)[1])
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def mrai_strategyfy(strategy:str, G: nx.DiGraph, value: float) -> nx.DiGraph:
    if strategy in mrai_strategies:
        eval("apply_" + strategy + "_strategy")(G, value)
    else:
        raise ValueError(f"Strategy \"{strategy}\" not available in {mrai_strategies}")

def set_node_mrai(G, node, mrai):
    for j in nx.neighbors(G, node):
        e = G.edges[(node, j)]
        e['mrai'] = round(float(mrai), 2)

def find_adv_node(G :nx.DiGraph):
    for node in G.nodes(data=True):
        if 'destinations' in node[1]:
            return node[0]

@mrai_strategy
def apply_constant_strategy(G :nx.DiGraph, value: float) -> None:
    nx.set_edge_attributes(G, value, "mrai")

@mrai_strategy
def apply_random_strategy(G: nx.DiGraph, value: float) -> None:
    for edge in G.edges(data=True):
        f = 0 + (value-0)*random.random()
        G.edges[(edge[0], edge[1])]['mrai'] = round(f, 3)

@mrai_strategy
def apply_dpc_strategy(G: nx.DiGraph, value:float) -> None:
    T = value  # max mrai in seconds
    adv_node = find_adv_node(G)
    cent = {i[0]: i[1]['centrality'] for i in G.nodes(data=True) }
    visited_nodes = set()
    set_node_mrai(G, adv_node, T*cent[adv_node]/2)
    fifo = set()
    for j in nx.neighbors(G, adv_node):
        fifo.add((adv_node, j))

    while len(fifo) > 0:
        i, j = fifo.pop()
        if j not in visited_nodes:
            e = G.edges[(i,j)]
            # Case j is the customer
            if str(e['policy']) == '2, 2, 2':  # we are in phase 3
                set_node_mrai(G, j, T*cent[j]/2)
            elif G.nodes[j]['type'] == 'T':  # we are in phase 1
                set_node_mrai(G, j, T/2)
                # set_node_mrai(G, j, T*cent[j]/2)
            else:  # we are in phase 3
                set_node_mrai(G, j, T*(2-cent[j])/2)
            visited_nodes.add(j)

            # Case i is the customer
            if str(e['policy']) == '0, inf, inf':
                for z in nx.neighbors(G, j):
                    if z != i and z not in visited_nodes:
                        fifo.add((j, z))
            else:
                for z in nx.neighbors(G, j):
                    if str(G.edges[(j, z)]['policy']) == '2, 2, 2' and z not in visited_nodes:
                        fifo.add((j, z))

@mrai_strategy
def apply_dpc2_strategy(G: nx.DiGraph, value:float) -> None:
    T = value  # max mrai in seconds
    adv_node = find_adv_node(G)
    cent = {i[0]: i[1]['centrality'] for i in G.nodes(data=True) }
    ss = max(cent.values())
    cent = {i: v/ss for i,v in cent.items()}

    visited_nodes = set()
    set_node_mrai(G, adv_node, T*cent[adv_node]/2)
    fifo = set()
    for j in nx.neighbors(G, adv_node):
        fifo.add((adv_node, j))

    while len(fifo) > 0:
        i, j = fifo.pop()
        if j not in visited_nodes:
            e = G.edges[(i,j)]
            # Case j is the customer
            if str(e['policy']) == '2, 2, 2':  # we are in phase 1
                set_node_mrai(G, j, T*cent[j]/2)
            elif G.nodes[j]['type'] == 'T':  # we are in phase 2
                set_node_mrai(G, j, T/2)
                # set_node_mrai(G, j, T*cent[j]/2)
            else:  # we are in phase 3
                set_node_mrai(G, j, T*(2-cent[j])/2)
            visited_nodes.add(j)

            # Case i is the customer
            if str(e['policy']) == '0, inf, inf':
                for z in nx.neighbors(G, j):
                    if z != i and z not in visited_nodes:
                        fifo.add((j, z))
            else:
                for z in nx.neighbors(G, j):
                    if str(G.edges[(j, z)]['policy']) == '2, 2, 2' and z not in visited_nodes:
                        fifo.add((j, z))

@mrai_strategy
def apply_reverse_dpc_strategy(G: nx.DiGraph, value:float) -> None:
    T = value  # max mrai in seconds
    adv_node = find_adv_node(G)
    cent = {i[0]: i[1]['centrality'] for i in G.nodes(data=True) }
    ss = max(cent.values())
    cent = {i: v/ss for i,v in cent.items()}

    visited_nodes = set()
    set_node_mrai(G, adv_node, T*cent[adv_node]/2)
    fifo = set()
    for j in nx.neighbors(G, adv_node):
        fifo.add((adv_node, j))

    while len(fifo) > 0:
        i, j = fifo.pop()
        if j not in visited_nodes:
            e = G.edges[(i,j)]
            # Case j is the customer
            if str(e['policy']) == '2, 2, 2':  # we are in phase 1
                set_node_mrai(G, j, T*(2-cent[j])/2)
            elif G.nodes[j]['type'] == 'T':  # we are in phase 2
                set_node_mrai(G, j, T/2)
                # Strange row removed
            else:  # we are in phase 3
                set_node_mrai(G, j, T*cent[j]/2)
            visited_nodes.add(j)

            # Case i is the customer
            if str(e['policy']) == '0, inf, inf':
                for z in nx.neighbors(G, j):
                    if z != i and z not in visited_nodes:
                        fifo.add((j, z))
            else:
                for z in nx.neighbors(G, j):
                    if str(G.edges[(j, z)]['policy']) == '2, 2, 2' and z not in visited_nodes:
                        fifo.add((j, z))

@mrai_strategy
def apply_centrality_strategy(G: nx.DiGraph, value:float) -> None:
    T = value  # max mrai in seconds
    adv_node = find_adv_node(G)
    cent = {i[0]: i[1]['centrality'] for i in G.nodes(data=True) }
    ss = max(cent.values())
    cent = {i: v/ss for i,v in cent.items()}

    for node in G.nodes:
        set_node_mrai(G, node, T*cent[node])

@mrai_strategy
def apply_banded_centrality_strategy(G: nx.DiGraph, value:float) -> None:
    T = value  # max mrai in seconds
    adv_node = find_adv_node(G)
    cent = {i[0]: i[1]['centrality'] for i in G.nodes(data=True) }
    ss = max(cent.values())
    cent = {i: v/ss for i,v in cent.items()}

    for node in G.nodes:
        set_node_mrai(G, node, T*round(cent[node], 1))

@mrai_strategy
def apply_reverse_centrality_strategy(G: nx.DiGraph, value:float) -> None:
    T = value  # max mrai in seconds
    adv_node = find_adv_node(G)
    cent = {i[0]: i[1]['centrality'] for i in G.nodes(data=True) }
    ss = max(cent.values())
    cent = {i: v/ss for i,v in cent.items()}

    for node in G.nodes:
        set_node_mrai(G, node, T*(1-cent[node]))

@mrai_strategy
def apply_reverse_banded_centrality_strategy(G: nx.DiGraph, value:float) -> None:
    T = value  # max mrai in seconds
    adv_node = find_adv_node(G)
    cent = {i[0]: i[1]['centrality'] for i in G.nodes(data=True) }
    ss = max(cent.values())
    cent = {i: v/ss for i,v in cent.items()}

    for node in G.nodes:
        set_node_mrai(G, node, T*(round(cent[node], 1)))

def adapt_to_mean(G, expected_mean):
    mean = 0.0
    n_elements = 0
    if expected_mean != 0.0:
        for e in G.edges(data=True):
            if e[2]['mrai'] != 0.0:
                mean += e[2]['mrai']
                n_elements += 1
        mean /= n_elements

        multiplier = round(float(expected_mean) / mean, 2)
        for e in G.edges(data=True):
            e[2]['mrai'] = round(e[2]['mrai'] * multiplier, 2)
    else:
        for e in G.edges(data=True):
            e[2]['mrai'] = 0.0

def main():
    options = parser.parse_args()

    random.seed(options.seed)
    
    G = nx.read_graphml(options.inputFile)
    mrai_strategyfy(options.type, G, options.default_mrai)
    if options.mean >= 0.0:
        adapt_to_mean(G, options.mean)
    nx.write_graphml(G, options.out)

if __name__ == "__main__":
    main()
