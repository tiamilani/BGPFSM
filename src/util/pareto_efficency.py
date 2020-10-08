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
import matplotlib.pyplot as plt

from plotter import Plotter, GeneralPlotter

parser = argparse.ArgumentParser(usage="python3 pareto_efficency.py [options]",
                        description="Analize an output file that describes "
                                  "the avg convergence time and the avg number "
                                  "of messages, one line is considered a compleate "
                                  "experimetn environment result",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="inputFile", default="general_avg.csv",
                    action="store", help="File to analize")
parser.add_argument("-o", "--output", dest="outputFile", default="paretoplot.pdf",
                    action="store", help="Where to save the results")
parser.add_argument("-r", "--render", dest="render", default=True,
                    action='store_false', help="Render the results on a pdf file in")

COLUMNS=["id", "avg_time", "avg_msg"]

def main():
    options = parser.parse_args()

    inputFile = options.inputFile

    df = pd.read_csv(inputFile, sep="|", index_col=COLUMNS[0])

    duplicateRowsDF = df[df.duplicated()]
    if len(duplicateRowsDF.index) > 0:
        print(duplicateRowsDF)

    if options.render:
        df.plot.scatter(x=COLUMNS[2], y=COLUMNS[1]);
        plt.savefig(options.outputFile, format="pdf")
        plt.close()

if __name__ == "__main__":
    main()
