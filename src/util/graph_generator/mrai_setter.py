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
parser.add_argument("-M", "--mean", dest="mean", default=0.0, action="store",
                  help="defines the default mean of mrais timers that need to be \
                        respected, with 0.0 the mean should not be evaluated", type=float)

mrai_strategies = []


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

@mrai_strategy
def apply_constant_strategy(G :nx.DiGraph, value: float) -> None:
    nx.set_edge_attributes(G, value, "mrai")

@mrai_strategy
def apply_random_strategy(G: nx.DiGraph, value: float) -> None:
    for edge in G.edges(data=True):
        G.edges[(edge[0], edge[1])]['mrai'] = round(random.uniform(0, value), 3)

def adapt_to_mean(G, expected_mean):
    mean = 0.0
    n_elements = 0
    for e in G.edges(data=True):
        if e[2]['mrai'] != 0.0:
            mean += e[2]['mrai']
            n_elements += 1
    mean /= n_elements

    multiplier = round(float(expected_mean) / mean, 2)
    for e in G.edges(data=True):
        e[2]['mrai'] = round(e[2]['mrai'] * multiplier, 2)

def main():
    options = parser.parse_args()

    random.seed(options.seed)
    
    G = nx.read_graphml(options.inputFile)
    mrai_strategyfy(options.type, G, options.default_mrai)
    if options.mean > 0.0:
        adapt_to_mean(G, options.mean)
    nx.write_graphml(G, options.out)

if __name__ == "__main__":
    main()
