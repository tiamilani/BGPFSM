#!/usr/bin/env python
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

import argparse
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
import milaniBGPLoad as DPC
import ipaddress

parser = argparse.ArgumentParser(usage="python3 study.py [options]",
                        description="Analize a graph file that describes "
                                  "an experiment environment",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="general_avg.csv",
                    action="store", help="File to analize")
parser.add_argument("-o", "--output", dest="outputFile", default="paretoplot.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-m", "--mrai_type", dest="mrai_type", default="random",
                    action='store', help="type of mrai used in the experiments")

def insert_destinations(graph: nx.Graph) -> None:
    node_networks = list(ipaddress.ip_network(u'100.0.0.0/8').subnets(new_prefix=24))

    i = 0
    for n in graph.nodes(data=True):
        if n[1]['type'] == 'C' or n[1]['type'] == 'CP' or n[1]['type'] == 'M':
            n[1]['destinations'] = str(node_networks[i])
        i += 1

def main():
    options = parser.parse_args()

    inputFile = options.inputFile

    G = nx.read_graphml(inputFile)
    be = nx.load_centrality(G, normalized=True)
    insert_destinations(G)
    dpc = DPC.mice_centrality(G, normalized=True)
    nx.set_node_attributes(G, be, "betweenness")
    nx.set_node_attributes(G, dpc, "DPC")
    sorted_be = sorted(be.items(), key=lambda x: x[1], reverse=True)

    nodes = [x[0] for x in sorted_be]
    centrality = [x[1] for x in sorted_be]
    dpc_centrality = [dpc[str(x)] for x in nodes]

    first_node_cent_0 = centrality.index(0.0)

    fig, ax = plt.subplots()

    l1 = ax.plot(nodes, centrality, label="Load centrality")
    l2 = ax.plot(nodes, dpc_centrality, label="DPC centrality")

    lns = l1 + l2 
    axes = [ax]

    labs = [l.get_label() for l in lns]
    # Shrink current axis's height by 10% on the bottom
    for ax in axes:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,
                         box.width, box.height * 0.95])
    # Put a legend below current axis
    axes[-1].legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
              fancybox=True, ncol=2)

    ax.set_xlabel("Nodes ordered by centrality")
    ax.set_ylabel("centrality normalized")
    ax.set_title("Nodes centrality correlation")

    ax.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    
    fig.savefig(options.outputFile, format="pdf")
    plt.close()

if __name__ == "__main__":
    main()

