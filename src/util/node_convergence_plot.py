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
from plotter import NodeConvergencePlotter

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

COLUMNS=["avg_conv_time", "std_conv_time", "avg_in_messages", "std_in_messages"]

def main():
    options = parser.parse_args()

    inputFile = options.inputFile

    df = pd.read_csv(inputFile, sep="|",
                    dtype={COLUMNS[0]: float,
                           COLUMNS[1]: float,
                           COLUMNS[2]: float,
                           COLUMNS[3]: float})

    p = NodeConvergencePlotter(df)
    p.plot(options.outputFile)

if __name__ == "__main__":
    main()
