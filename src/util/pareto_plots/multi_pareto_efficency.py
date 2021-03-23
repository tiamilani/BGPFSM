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

parser = argparse.ArgumentParser(usage="python3 multi_pareto_efficency.py [options]",
                        description="Analize  the output of multiple files that describes "
                                  "the avg convergence time and the avg number "
                                  "of messages, one line is considered a compleate "
                                  "experiment environment result",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="general_avg.csv",
                    action="store", nargs='+', help="Files to analize")
parser.add_argument("-o", "--output", dest="outputFile", default="paretoplot.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-r", "--render", dest="render", default=True,
                    action='store_false', help="Render the results on a pdf file in")

COLUMNS=["id", "mrai" ,"avg_time", "avg_msg"]

xmin=200
ymin=0
xmax=450
ymax=600

def check_limits(df: pd.DataFrame) -> None:
    x_min = df[df[COLUMNS[3]] < xmin]
    x_max = df[df[COLUMNS[3]] > xmax]
    y_min = df[df[COLUMNS[2]] < ymin]
    y_max = df[df[COLUMNS[2]] > ymax]
    if len(x_min.index) > 0:
        print("Errors, values under the x threshold")
    if len(x_max.index) > 0:
        print("Errors, values over the x threshold")
    if len(y_min.index) > 0:
        print("Errors, values under the y threshold")
    if len(y_max.index) > 0:
        print(y_max)
        print("Errors, values over the y threshold")

def main():
    options = parser.parse_args()

    ax = None
    colors = plt.rcParams["axes.prop_cycle"]()
    for _file in options.inputFile:
        file_name=_file.split('/')[-1].split('.')[0]
        scatter_label=file_name.split('_')[1]

        df = pd.read_csv(_file, sep="|", index_col=COLUMNS[0])

        if options.render:
            c = next(colors)["color"]
            if ax is None:
                ax = df.plot.scatter(x=COLUMNS[3], y=COLUMNS[2], label=scatter_label, c='b')
            else:
                df.plot.scatter(x=COLUMNS[3], y=COLUMNS[2], ax=ax, label=scatter_label, c=c)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                     box.width, box.height * 0.9])
    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
              fancybox=True, ncol=3)

    ax.set_xlabel("Messages transmitted")
    ax.set_ylabel("Convergence time [s]")
    plt.title("Distribution comparison")

    plt.savefig(options.outputFile, format="pdf")
    plt.close()

if __name__ == "__main__":
    main()
