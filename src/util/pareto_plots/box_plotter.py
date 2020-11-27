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

COLUMNS=["id", "file_name", "convergence_time", "total_messages"]

def main():
    options = parser.parse_args()
    time_df = pd.DataFrame()
    messages_df = pd.DataFrame()

    output_file = options.outputFile.split('.')[0]
    
    for _file in options.inputFile:
        file_name=_file.split('/')[-1].split('-')[0]

        df = pd.read_csv(_file, sep="|", index_col=COLUMNS[0])

        time_df[file_name] = df[COLUMNS[2]].values
        messages_df[file_name] = df[COLUMNS[3]].values

    plotter.plot_boxplot_pandasDataframe(time_df, title = "Convergence time comparison",
                                         ylabel="Convergence time [s]",
                                         output_file_name=output_file+"_time_boxplot.pdf")
    plotter.plot_boxplot_pandasDataframe(messages_df, title = "Total messages comparison",
                                         ylabel="# Messages",
                                         output_file_name=output_file+"_messages_boxplot.pdf")

if __name__ == "__main__":
    main()