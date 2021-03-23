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
from plotter import simple_plotter
import pickle
import os.path
import math
from matplotlib.lines import Line2D

parser = argparse.ArgumentParser(usage="python3 pareto_efficency.py [options]",
                        description="Analize an output file that describes "
                                  "the avg convergence time and the avg number "
                                  "of messages, one line is considered a compleate "
                                  "experiment environment result",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="general_avg.csv",
                    action="store", help="File to analize", nargs="+")
parser.add_argument("-o", "--output", dest="outputFile", default="avg_convergence_plot.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-l", "--limit", dest="limits", default=0, type=int,
                    action="store", help="y-axis limit")
parser.add_argument("-lm", "--limit_msg", dest="limit_msg", default=0, type=int,
                    action="store", help="y-msg-axis limit")

def main():
    options = parser.parse_args()
    markers = list(Line2D.markers.keys())

    if '/' in options.outputFile:
        outp_path = options.outputFile.rsplit('/', 1)[0] + "/"
        out_name = options.outputFile.rsplit('/', 1)[1].rsplit('.', 1)[0]
    else:
        outp_path = ""
        out_name = options.outputFile.rsplit('.', 1)[0]

    levels = {}

    for f in options.inputFile:
        file_name = f.rsplit('/', 1)[-1].split('.')[0]
        level = math.floor((int(file_name.split('-')[-1].split('l')[-1])+1)%4)
        if level == 0:
            level = 4
        print("{} -> {}".format(file_name,level))
        if level not in levels:
            levels[level] = [f]
        else:
            levels[level].append(f)

    print(levels)
    levels_df = {}
    for level in levels:
        for f in levels[level]:
            level_df = pd.read_csv(f, index_col="group")
            if level not in levels_df:
                levels_df[level] = [level_df]
            else:
                levels_df[level].append(level_df)

    #for level in levels_df:
    #    max_group = 0
    #    for df in levels_df[level]:
    #        if max_group < int(df.index.max()):
    #            max_group = int(df.index.max())
    #    for df in levels_df[level]:
    #        actual_level = int(df.index.max())
    #        while actual_level < max_group:
    #            actual_level += 1
    #            df.loc[actual_level] = [0,0,0]

    levels_mean = {}
    for level in levels_df:
        concat_df = None
        for df in levels_df[level]:
            if concat_df is None:
                concat_df = df
            else:
                concat_df = pd.concat((concat_df, df))
        df_means = concat_df.groupby(concat_df.index).mean()
        levels_mean[level] = df_means

    fig_time, ax_time = simple_plotter.get_axes()
    ax2_time = ax_time.twinx()
    fig_msg, ax_msg = simple_plotter.get_axes()
    ax2_msg = ax_msg.twinx()
    time_labels = None
    msg_labels = None
    i = 1
    for level in levels_mean:
        i += 1
        df = levels_mean[level]
        l_time_cent = simple_plotter.plot_line(df.index.values, df.avg_centr.values, 'b', label="Level " + str(level) + " avg centrality", ax=ax_time, marker=markers[i])
        l_msg_cent = simple_plotter.plot_line(df.index.values, df.avg_centr.values, 'b', label="Level " + str(level) + " avg centrality", ax=ax_msg, marker=markers[i])
        l_time_time = simple_plotter.plot_line(df.index.values, df.avg_time.values, 'g', label="Level " + str(level) + " avg convergence time", ax=ax2_time, marker=markers[i])
        l_msg_msg = simple_plotter.plot_line(df.index.values, df.avg_msg.values, 'purple', label="Level " + str(level) + " avg Messages to converge", ax=ax2_msg, marker=markers[i])

        if time_labels is None:
            time_labels = l_time_cent + l_time_time
        else:
            time_labels += l_time_cent + l_time_time
        if msg_labels is None:
            msg_labels = l_msg_cent + l_msg_msg
        else:
            msg_labels += l_msg_cent + l_msg_msg
    
    lgd_time = simple_plotter.legends(time_labels, [ax_time, ax2_time])
    lgd_msg = simple_plotter.legends(msg_labels, [ax_msg, ax2_msg])

    simple_plotter.ax_set_labels(ax_time,ylabel="AVG Centrality",xlabel="groups")
    simple_plotter.ax_set_labels(ax2_time,ylabel="AVG Convergence time[s]")
    simple_plotter.ax_set_labels(ax_msg,ylabel="AVG Centrality",xlabel="groups")
    simple_plotter.ax_set_labels(ax2_msg,ylabel="AVG Messages necessary to reach convergence")

    if options.limits > 0:
        ax2_time.set_ylim(0, options.limits)
    if options.limit_msg > 0:
        ax2_msg.set_ylim(0, options.limit_msg)

    fig_time.savefig(options.outputFile.rsplit('.', 1)[0] + "_centVStime.pdf", format="pdf",
                    bbox_extra_artists=(lgd_time,), bbox_inches='tight')
    fig_msg.savefig(options.outputFile.rsplit('.', 1)[0] + "_centVSmsg.pdf", format="pdf",
                    bbox_extra_artists=(lgd_msg,), bbox_inches='tight')

if __name__ == "__main__":
    main()
