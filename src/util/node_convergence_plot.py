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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from plotter import NodeConvergencePlotter
import pickle
import os.path

parser = argparse.ArgumentParser(usage="python3 pareto_efficency.py [options]",
                        description="Analize an output file that describes "
                                  "the avg convergence time and the avg number "
                                  "of messages, one line is considered a compleate "
                                  "experiment environment result",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="general_avg.csv",
                    action="store", help="File to analize")
parser.add_argument("-o", "--output", dest="outputFile", default="avg_convergence_plot.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-l", "--limit", dest="limits", default=0, type=int,
                    action="store", help="y-axis limit")
parser.add_argument("-lm", "--limit_msg", dest="limit_msg", default=0, type=int,
                    action="store", help="y-msg-axis limit")
parser.add_argument("-d", "--diameter", dest="diame", default=0, type=int,
                    action="store", help="diameter increment")
parser.add_argument("-g", "--graph", dest="graph", default=None, 
                    action="store", help="Graph containing nodes centrality values, \
                                          used to plot the node convergence \
                                          time in relation of the centrality")

COLUMNS=["avg_conv_time", "std_conv_time", "avg_in_messages", "std_in_messages",
         "avg_suppressed_routes", "std_suppressed_routes"]

def get_all_paths(G, src, dst, cutoff):
    return nx.all_simple_paths(G, source=src, target=dst, cutoff=cutoff)

def shortest_valid_path(G, paths):
    customer = "0, inf, inf"
    peer = "1, inf, inf"
    servicer = "2, 2, 2"
    valid_path = []
    paths = sorted(list(paths), key=len)
    for path in map(nx.utils.pairwise, paths):
        valid = True
        previous_policy = None
        path = list(path)
        # print("path: ", path)
        for edge in path:
            policy = G[edge[0]][edge[1]]['policy']
            # print("Edge: ", edge, policy, previous_policy)
            if previous_policy is None:
                previous_policy = policy
            if previous_policy == customer:
                # If I get something from a client every
                # direction is valid
                previous_policy = policy
            elif previous_policy == peer or previous_policy == servicer:    
                # If I get something from a peer or a servicer then
                # only servicer links are valid
                if policy != servicer:
                    # print("Invalid")
                    valid = False
                    break
        if valid:
            valid_path = path
            return valid_path
    if len(valid_path) == 0:
        print("ERROR, NO VALID PATHS FOUND")
        exit(1)

def main():
    options = parser.parse_args()

    if '/' in options.outputFile:
        outp_path = options.outputFile.rsplit('/', 1)[0] + "/"
        out_name = options.outputFile.rsplit('/', 1)[1].rsplit('.', 1)[0]
    else:
        outp_path = ""
        out_name = options.outputFile.rsplit('.', 1)[0]
    inputFile = options.inputFile

    df = pd.read_csv(inputFile, sep="|",
                    dtype={COLUMNS[0]: float,
                           COLUMNS[1]: float,
                           COLUMNS[2]: float,
                           COLUMNS[3]: float,
                           COLUMNS[4]: float,
                           COLUMNS[5]: float})

    G = nx.read_graphml(options.graph)
    centrality=nx.get_node_attributes(G, 'centrality')
    ss = max(centrality.values())
    centrality = {i: v/ss for i,v in centrality.items()}
    source_node = list(nx.get_node_attributes(G, 'destinations').keys())[0]
    hops = {}

    pkl_name = outp_path + options.graph.rsplit('/', 1)[1].split('.')[0]
    print(pkl_name)
    if os.path.isfile(pkl_name + '.pkl'):
        filehandler = open(pkl_name + '.pkl', 'rb')
        hops = pickle.load(filehandler)
    else:
        hops[source_node] = 0
        diameter = nx.diameter(G) + options.diame
        for node in G.nodes:
            print(node)
            if node != source_node:
                paths = get_all_paths(G, source_node, node, diameter)
                paths = shortest_valid_path(G, paths)
                hops[node] = len(paths)

        file_pi = open(pkl_name + '.pkl', 'wb')
        pickle.dump(hops, file_pi)

    ordered_hops = {key: value for (key, value) in sorted(hops.items(), key=lambda x: x[1])}

    actual_dist = 0
    groups = [[]]
    for node in ordered_hops:
        if ordered_hops[node] > actual_dist:
            actual_dist = ordered_hops[node]
            groups.append([])
        groups[-1].append((node, centrality[node]))

    ordered_hops = {}
    for group in groups:
        group.sort(key=lambda x: x[1], reverse=True)
        for node in group:
            ordered_hops[node[0]] = hops[node[0]]

    group_hops = list(range(len(groups)))

    p = NodeConvergencePlotter(df, centrality)
    p.plot(options.outputFile, limit=options.limits)
    avg_time, avg_cent = p.plot_centrality_vs_convergence(options.outputFile, ordered_hops, limit=options.limits)
    avg_msg = p.plot_centrality_vs_messages(options.outputFile, ordered_hops, limit=options.limit_msg)
    avg_sup = p.plot_centrality_vs_suppressions(options.outputFile, ordered_hops, limit=options.limit_msg)

    data = list(zip(group_hops, avg_cent, avg_time, avg_msg, avg_sup))
    df = pd.DataFrame(data, columns = ['group', 'avg_centr', 'avg_time', 'avg_msg', 'avg_sup'])
    df = df.set_index('group')
    df.to_csv(outp_path + out_name.rsplit('_',2)[0] + ".csv", index = True)

if __name__ == "__main__":
    main()
