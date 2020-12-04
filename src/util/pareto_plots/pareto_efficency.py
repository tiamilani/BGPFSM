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
import plotter

parser = argparse.ArgumentParser(usage="python3 pareto_efficency.py [options]",
                        description="Analize an output file that describes "
                                  "the avg convergence time and the avg number "
                                  "of messages, one line is considered a compleate "
                                  "experiment environment result",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="general_avg.csv",
                    action="store", help="File to analize")
parser.add_argument("-o", "--output", dest="outputFile", default="paretoplot.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-r", "--render", dest="render", default=True,
                    action='store_false', help="Render the results on a pdf file in")
parser.add_argument("-m", "--mrai_type", dest="mrai_type", default="random",
                    action='store', help="type of mrai used in the experiments")

COLUMNS=["id", "mrai" ,"avg_time", "avg_msg", "avg_suppressions", "n95_perc_time", 
         "n05_perc_time", "std_time",
         "n95_perc_msg", "n05_perc_msg", "std_msg", 
         "n95_perc_sup", "n05_perc_sup", "std_sup"]
xmin=200
ymin=0
xmax=450
ymax=200

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
        print("Errors, values over the y threshold")


# Faster than is_pareto_efficient_simple, but less readable.
def is_pareto_efficient(costs, return_mask = True):
    """
    Find the pareto-efficient points
    :param costs: An (n_points, n_costs) array
    :param return_mask: True to return a mask
    :return: An array of indices of pareto-efficient points.
        If return_mask is True, this will be an (n_points, ) boolean array
        Otherwise it will be a (n_efficient_points, ) integer array of indices.
    """
    is_efficient = np.arange(costs.shape[0])
    n_points = costs.shape[0]
    next_point_index = 0  # Next index in the is_efficient array to search for
    while next_point_index<len(costs):
        nondominated_point_mask = np.any(costs<costs[next_point_index], axis=1)
        nondominated_point_mask[next_point_index] = True
        is_efficient = is_efficient[nondominated_point_mask]  # Remove dominated points
        costs = costs[nondominated_point_mask]
        next_point_index = np.sum(nondominated_point_mask[:next_point_index])+1
    if return_mask:
        is_efficient_mask = np.zeros(n_points, dtype = bool)
        is_efficient_mask[is_efficient] = True
        return is_efficient_mask
    else:
        return is_efficient

def main():
    options = parser.parse_args()

    inputFile = options.inputFile

    df = pd.read_csv(inputFile, sep="|", index_col=COLUMNS[0])

    #check_limits(df)

    duplicateRowsDF = df[df.duplicated()]
    if len(duplicateRowsDF.index) > 0:
        print("Warning, there are some duplicates")

    points=np.column_stack([df[COLUMNS[2]].values, df[COLUMNS[3]].values])
    pareto_front=df.iloc[is_pareto_efficient(points, return_mask=False)]

    out_name = options.outputFile.split('.')[0]

    if options.render:
        plotter.plot_scatter(df[COLUMNS[3]].values, df[COLUMNS[2]].values, 
                             pareto_front=(pareto_front[COLUMNS[3]].values, pareto_front[COLUMNS[2]].values),
                             label=str(options.mrai_type) + " MRAI experiments",
                             xlabel="Messages transmitted", ylabel="Convergence time",
                             title="Experiments efficency",
                             output_file_name= out_name+".pdf")

        allowed_types = ["constant", "dpc", "dpc2", "reverse_dpcc"]
        if options.mrai_type in allowed_types:
            plotter.plot_messages_time_comparison(df[COLUMNS[1]].values,
                                                  df[COLUMNS[2]].values, df[COLUMNS[3]].values,
                                                  title="MRAI " + options.mrai_type + " performances",
                                                  output_file_name=out_name+"_mrai_evolution.pdf")

            plotter.plot_messages_suppression_time_comparison(df[COLUMNS[1]].values,
                                                  df[COLUMNS[2]].values, df[COLUMNS[3]].values,
                                                  df[COLUMNS[4]].values,
                                                  title="MRAI + RFD " + options.mrai_type + " performances",
                                                  output_file_name=out_name+"_mrai_rfd_evolution.pdf")

            plotter.plot_messages_time_comparison_error_bars(df[COLUMNS[1]].values,
                    df[COLUMNS[2]].values, df[COLUMNS[3]].values, df[COLUMNS[6]].values,
                    df[COLUMNS[9]].values, title = "MRAI " + options.mrai_type + " performances " +
                    "with Std deviation", output_file_name=out_name+"_mrai_evolution_std.pdf")

            plotter.plot_messages_time_comparison_error_bars_alpha(df[COLUMNS[1]].values,
                    df[COLUMNS[2]].values, df[COLUMNS[3]].values, df[COLUMNS[6]].values,
                    df[COLUMNS[9]].values, title = "MRAI " + options.mrai_type + " performances " +
                    "with Std deviation", output_file_name=out_name+"_mrai_evolution_std_alpha.pdf")

if __name__ == "__main__":
    main()
