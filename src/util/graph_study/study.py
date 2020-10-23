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

parser = argparse.ArgumentParser(usage="python3 study.py [options]",
                        description="Analize a graph file that describes "
                                  "an experiment environment",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="general_avg.csv",
                    action="store", help="File to analize",  nargs='+')
parser.add_argument("-o", "--output", dest="outputFile", default="paretoplot.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-m", "--mrai_type", dest="mrai_type", default="random",
                    action='store', help="type of mrai used in the experiments")

def main():
    options = parser.parse_args()

    inputFiles = options.inputFile

    out_mrai = []
    in_mrai = []
    diff_mrai = []

    for _file in inputFiles:
        G = nx.read_graphml(_file)
        be = nx.load_centrality(G, normalized=True)
        nx.set_node_attributes(G, be, "betweenness")
        sorted_be = sorted(be.items(), key=lambda x: x[1], reverse=True)

        nodes = [x[0] for x in sorted_be]
        avg_out_mrai = []
        avg_in_mrai = []
        reverse_of_mrai_difference = []

        for node in nodes:
            edges = G.out_edges(node, data=True)
            mrai = 0
            for edge in edges:
                mrai += edge[2]['mrai']
            mrai /= len(edges)
            avg_out_mrai.append(mrai)

        for node in nodes:
            edges = G.in_edges(node, data=True)
            mrai = 0
            for edge in edges:
                mrai += edge[2]['mrai']
            mrai /= len(edges)
            avg_in_mrai.append(mrai)

        avg_out_mrai_norm = [x/max(avg_out_mrai) for x in avg_out_mrai]
        avg_in_mrai_norm = [x/max(avg_in_mrai) for x in avg_in_mrai]

        reverse_of_mrai_difference = [abs(avg_out_mrai_norm[i] - avg_in_mrai_norm[i]) \
                                      for i in range(len(avg_out_mrai_norm))]

        if len(out_mrai) == 0:
            out_mrai = [[x] for x in avg_out_mrai_norm]
        else:
            for x, y in zip(avg_out_mrai_norm, out_mrai):
                y.append(x)
        if len(in_mrai) == 0:
            in_mrai = [[x] for x in avg_in_mrai_norm]
        else:
            for x, y in zip(avg_in_mrai_norm, in_mrai):
                y.append(x)
        if len(diff_mrai) == 0:
            diff_mrai = [[x] for x in reverse_of_mrai_difference]
        else:
            for x, y in zip(reverse_of_mrai_difference, diff_mrai):
                y.append(x)

    nodes = [x[0] for x in sorted_be]
    centrality = [x[1] for x in sorted_be]
    first_node_cent_0 = centrality.index(0.0)

    assert len(out_mrai[0]) == len(inputFiles)

    out_mrai_mean = [statistics.mean(x) for x in out_mrai]
    out_mrai_std = [statistics.stdev(x) for x in out_mrai]
    in_mrai_mean = [statistics.mean(x) for x in in_mrai]
    in_mrai_std = [statistics.stdev(x) for x in in_mrai]
    diff_mrai_mean = [statistics.mean(x) for x in diff_mrai]
    diff_mrai_std = [statistics.stdev(x) for x in diff_mrai]

    assert len(out_mrai_mean) == len(nodes)

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    ax1_1 = ax1.twinx()
    ax2_2 = ax2.twinx()
    ax3_3 = ax3.twinx()

    l1 = ax1.plot(nodes, centrality, label="Load centrality")
    l2 = ax1_1.plot(nodes, out_mrai_mean, 'r', label="outgoing mean mrai")
    ax1_1.axvline(x=first_node_cent_0, c="grey")
    out_mrai_std_y1 = [x + y for x, y in zip(out_mrai_mean, out_mrai_std)]
    out_mrai_std_y2 = [x - y for x, y in zip(out_mrai_mean, out_mrai_std)]
    ax1_1.fill_between(nodes, out_mrai_std_y1, out_mrai_std_y2, facecolor='r', alpha=0.3)

    ax2.plot(nodes, centrality, label="Load centrality")
    l3 = ax2_2.plot(nodes, in_mrai_mean, 'g', label="ingoing mean mrai")
    ax2_2.axvline(x=first_node_cent_0, c="grey")
    in_mrai_std_y1 = [x + y for x, y in zip(in_mrai_mean, in_mrai_std)]
    in_mrai_std_y2 = [x - y for x, y in zip(in_mrai_mean, in_mrai_std)]
    ax2_2.fill_between(nodes, in_mrai_std_y1, in_mrai_std_y2, facecolor='g', alpha=0.3)

    ax3.plot(nodes, centrality, label="Load centrality")
    l4 = ax3_3.plot(nodes, diff_mrai_mean, color="purple", label="Ingoing/outgoing MRAI difference")
    ax3_3.axvline(x=first_node_cent_0, c="grey")
    diff_mrai_std_y1 = [x + y for x, y in zip(diff_mrai_mean, diff_mrai_std)]
    diff_mrai_std_y2 = [x - y for x, y in zip(diff_mrai_mean, diff_mrai_std)]
    ax3_3.fill_between(nodes, diff_mrai_std_y1, diff_mrai_std_y2, facecolor='purple', alpha=0.3)

    lns = l1 + l2 + l3 + l4
    axes = [ax1, ax1_1, ax2, ax2_2, ax3, ax3_3]

    labs = [l.get_label() for l in lns]
    # Shrink current axis's height by 10% on the bottom
    for ax in axes:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,
                         box.width, box.height * 0.95])
    # Put a legend below current axis
    axes[-1].legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
              fancybox=True, ncol=2)

    ax1.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    ax2.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    ax3.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off

    ax3.set_xlabel("Nodes ordered by centrality")
    ax2.set_ylabel("Load centrality normalized")
    ax2_2.set_ylabel("MRAI normalized")
    ax1.set_title("Nodes centrality MRAI correlation")

    fig.savefig(options.outputFile, format="pdf")
    plt.close()
    
if __name__ == "__main__":
    main()
