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
import matplotlib
import matplotlib.pyplot as plt
import plotter
from matplotlib.lines import Line2D

parser = argparse.ArgumentParser(usage="python3 multi_folders.py [options]",
                        description="Analize multiple output files in their folders "
                                  "get the avg convergence time and the avg number "
                                  "of messages, one line is considered a compleate "
                                  "experiment environment result",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--folder", dest="inputFolder", default=".",
                    action="store", help="folder to analize", nargs="+")
parser.add_argument("-fn", "--filename", dest="file_name", default="general_avg.csv",
                    action="store", help="Where to save the results")
parser.add_argument("-o", "--output", dest="outputFile", default="multi_folder.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-r", "--render", dest="render", default=True,
                    action='store_false', help="Render the results on a pdf file in")
parser.add_argument("--tmin", dest="time_min", default=None, action="store",
                    type=int, help="min time range for the plot")
parser.add_argument("--tmax", dest="time_max", default=None, action="store",
                    type=int, help="Max time range for the plot")
parser.add_argument("--mmin", dest="messages_min", default=None, action="store",
                    type=int, help="min messages range for the plot")
parser.add_argument("--mmax", dest="messages_max", default=None, action="store",
                    type=int, help="Max messages range for the plot")
parser.add_argument("--rmin", dest="rfd_min", default=None, action="store",
                    type=int, help="min rfd range for the plot")
parser.add_argument("--rmax", dest="rfd_max", default=None, action="store",
                    type=int, help="Max rfd range for the plot")
parser.add_argument("-fs", "--fontsize", dest="font_size", default=None,
                    action="store", type=int, help="Redefine the font size")

COLUMNS = ["id", "mrai","avg_time", "avg_msg", "avg_suppressions", "n95_perc_time", "n05_perc_time", "std_time",
         "n95_perc_msg", "n05_perc_msg", "std_msg", "n95_perc_sup", "n05_perc_sup", "std_sup"]

def set_ylimits(ax, lower_bound, upper_bound):
    if lower_bound is None:
        lower_bound = ax.get_ylim()[0]
    if upper_bound is None:
        upper_bound = ax.get_ylim()[1]
    ax.set_ylim(lower_bound, upper_bound)

def main():
    options = parser.parse_args()

    ax = None
    fig = None
    l_list = {}
    colors = plt.rcParams["axes.prop_cycle"]()
    markers = list(Line2D.markers.keys())
    types = {}
    marks = {}

    mean_df = pd.DataFrame(columns=["MRAI"], dtype=float)

    for folder in options.inputFolder:
        file_path = folder + "/" + options.file_name
        folder_name = folder.split('/')[-1]
        _type = folder_name.rsplit('-', 1)[0].rsplit('-', 1)[-1]
        time_column = _type + "_time"
        msgs_column = _type + "_msgs"
        if _type not in types:
            types[_type] = (next(colors)["color"], next(colors)["color"])
            marks[_type] = (markers[0], markers[1])
            markers.remove(marks[_type][0])
            markers.remove(marks[_type][1])
            mean_df[time_column] = None
            mean_df[msgs_column] = None

        df = pd.read_csv(file_path, sep="|", index_col=COLUMNS[0])
        df = df.drop(COLUMNS[4::], axis=1)
        df = df.rename(columns = {COLUMNS[1]:"MRAI", COLUMNS[2]: time_column, COLUMNS[3]: msgs_column})
        mean_df = pd.concat([mean_df, df], ignore_index=True)
        df = df.rename(columns = {"MRAI": COLUMNS[1], time_column: COLUMNS[2], msgs_column: COLUMNS[3]})

        if options.render:
            if ax is None:
                fig, ax = plotter.get_axes()
                ax2 = ax.twinx()
                l1 = plotter.plot_line(df[COLUMNS[1]], df[COLUMNS[2]], types[_type][0],
                                       label="Conv. time " + _type, ax=ax,
                                       marker=marks[_type][0])
                l2 = plotter.plot_line(df[COLUMNS[1]], df[COLUMNS[3]], types[_type][1],
                                       label="# Messages " + _type, ax=ax2,
                                       marker=marks[_type][1])
                if str(_type) not in l_list.keys():
                    l_list[_type + "_time"] = l1
                    l_list[_type + "_msgs"] = l2
            else:
                l1 = plotter.plot_line(df[COLUMNS[1]], df[COLUMNS[2]], types[_type][0],
                                       label="Conv. time " + _type, ax=ax,
                                       marker=marks[_type][0])
                l2 = plotter.plot_line(df[COLUMNS[1]], df[COLUMNS[3]], types[_type][1],
                                       label="# Messages " + _type, ax=ax2,
                                       marker=marks[_type][1])
                if str(l1) not in l_list.keys():
                    l_list[_type + "_time"] = l1
                    l_list[_type + "_msgs"] = l2

    lns = None
    l_keys = l_list.keys()
    l_keys = [x[::-1] for x in l_keys]
    l_keys = sorted(l_keys)
    l_keys = [x[::-1] for x in l_keys]
    for l in l_keys:
        if lns is None:
            lns = l_list[l]
        else:
            lns += l_list[l]


    # Set general font size
    actual_fs = plt.rcParams['font.size']
    ax2.set_yscale("log")
    if options.font_size is not None:
        plt.rcParams['font.size'] = str(options.font_size)
        # Set tick font size
        for label in (ax.get_xticklabels() + ax.get_yticklabels() + ax2.get_yticklabels()):
            label.set_fontsize(options.font_size)
    else:
        options.font_size = actual_fs

    lgd = plotter.legends(lns, [ax, ax2])
    ax.set_xlabel("MRAI value", fontsize=options.font_size)
    ax.set_ylabel("Convergence time [s]", fontsize=options.font_size)
    ax2.set_ylabel("# Packets", fontsize=options.font_size)
    plt.title("MRAI evolution")
    set_ylimits(ax, options.time_min, options.time_max)
    set_ylimits(ax2, options.messages_min, options.messages_max)
    #ax2.set_yticks([10000, 20000, 30000, 40000, 50000, 60000])
    #ax2.get_yaxis().set_major_formatter(plt.LogFormatter(10,  labelOnlyBase=False))
    #ax2.get_yaxis().get_major_formatter().labelOnlyBase = False

    out_name = options.outputFile.rsplit('.', 1)[0]
    fig.savefig(out_name + "_all.pdf", format="pdf", bbox_extra_artists=(lgd,), bbox_inches='tight')
    #plt.savefig(out_name + "_all.pdf", format="pdf")
    plt.close()

    fig, ax = plotter.get_axes()
    ax2 = ax.twinx()

    columns = mean_df.columns[1::]
    it = iter(columns)

    l_list = {}

    for column in it:
        c1 = column
        c2 = next(it)
        tmp_df = mean_df[["MRAI", c1, c2]]
        tmp_df = tmp_df.dropna()
        tmp_df = tmp_df.groupby(["MRAI"]).mean()

        _type = c1.rsplit('_', 1)[0]
        l1 = plotter.plot_line(tmp_df.index, tmp_df[c1], types[_type][0],
                               label="Mean Conv. time " + _type, ax=ax,
                               marker = marks[_type][0])
        l2 = plotter.plot_line(tmp_df.index, tmp_df[c2], types[_type][1],
                               label="Mean # Messages " + _type, ax=ax2,
                               marker = marks[_type][1])

        if str(l1) not in l_list.keys():
            l_list[_type + "_time"] = l1
            l_list[_type + "_msgs"] = l2

    lns = None
    l_keys = l_list.keys()
    l_keys = [x[::-1] for x in l_keys]
    l_keys = sorted(l_keys)
    l_keys = [x[::-1] for x in l_keys]
    for l in l_keys:
        if lns is None:
            lns = l_list[l]
        else:
            lns += l_list[l]


    # Set general font size
    actual_fs = plt.rcParams['font.size']
    ax2.set_yscale("log")
    if options.font_size is not None:
        plt.rcParams['font.size'] = str(options.font_size)
        # Set tick font size
        for label in (ax.get_xticklabels() + ax.get_yticklabels() + ax2.get_yticklabels()):
            label.set_fontsize(options.font_size)
    else:
        options.font_size = actual_fs

    lgd = plotter.legends(lns, [ax, ax2])
    ax.set_xlabel("MRAI value", fontsize=options.font_size)
    ax.set_ylabel("Convergence time [s]", fontsize=options.font_size)
    ax2.set_ylabel("# Packets", fontsize=options.font_size)
    plt.title("MRAI evolution")
    set_ylimits(ax, options.time_min, options.time_max)
    set_ylimits(ax2, options.messages_min, options.messages_max)
    #ax2.set_yticks([10000, 20000, 30000, 40000, 50000, 60000])
    #ax2.get_yaxis().set_major_formatter(plt.LogFormatter(10,  labelOnlyBase=False))
    #ax2.get_yaxis().get_major_formatter().labelOnlyBase = False

    out_name = options.outputFile.rsplit('.', 1)[0]
    fig.savefig(out_name + "_mean.pdf", format="pdf", bbox_extra_artists=(lgd,), bbox_inches='tight')
    #plt.savefig(out_name + "_mean.pdf", format="pdf")
    plt.close()

    ax = None
    fig = None
    l_list = {}
    colors = plt.rcParams["axes.prop_cycle"]()
    markers = list(Line2D.markers.keys())
    types = {}
    marks = {}
    # RFD comparison plot
    for folder in options.inputFolder:
        file_path = folder + "/" + options.file_name
        folder_name = folder.split('/')[-1]
        _type = folder_name.rsplit('-', 1)[0].rsplit('-', 1)[-1]
        rfd_column = _type + "_rfd"
        if _type not in types:
            types[_type] = next(colors)["color"]
            marks[_type] = markers[0]
            markers.remove(marks[_type])
            mean_df[rfd_column] = None

        df = pd.read_csv(file_path, sep="|", index_col=COLUMNS[0])
        df = df.drop(COLUMNS[5::], axis=1)
        df = df.drop(COLUMNS[2:4], axis=1)
        df = df.rename(columns = {COLUMNS[1]:"MRAI", COLUMNS[4]: rfd_column})

        if options.render:
            if ax is None:
                fig, ax = plotter.get_axes()
                l1 = plotter.plot_line(df["MRAI"], df[rfd_column], types[_type],
                                       label="Suppressed routes " + _type, ax=ax,
                                       marker = marks[_type])
                if str(_type) not in l_list.keys():
                    l_list[_type + "_sup"] = l1
            else:
                l1 = plotter.plot_line(df["MRAI"], df[rfd_column], types[_type],
                                       label="Suppressed routes " + _type, ax=ax,
                                       marker = marks[_type])
                if str(l1) not in l_list.keys():
                    l_list[_type + "_sup"] = l1

    lns = None
    l_keys = l_list.keys()
    l_keys = [x[::-1] for x in l_keys]
    l_keys = sorted(l_keys)
    l_keys = [x[::-1] for x in l_keys]
    for l in l_keys:
        if lns is None:
            lns = l_list[l]
        else:
            lns += l_list[l]

    # Set general font size
    actual_fs = plt.rcParams['font.size']
    lgd = plotter.legends(lns, [ax])
    if options.font_size is not None:
        plt.rcParams['font.size'] = str(options.font_size)
        # Set tick font size
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontsize(options.font_size)
    else:
        options.font_size = actual_fs

    ax.set_xlabel("MRAI value", fontsize=options.font_size)
    ax.set_ylabel("Suppressed routes", fontsize=options.font_size)
    plt.title("MRAI suppression evolution")
    set_ylimits(ax, options.rfd_min, options.rfd_max)

    out_name = options.outputFile.rsplit('.', 1)[0]
    fig.savefig(out_name + "_rfd_all.pdf", format="pdf", bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()



if __name__ == "__main__":
    main()
