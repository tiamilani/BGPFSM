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

import pandas as pd
import matplotlib.pyplot as plt

file1 = "results/fabrikant/fabrikant-nomrai/general_study.csv"
file2 = "results/fabrikant/fabrikant-30fixed/general_study.csv"
file3 = "results/fabrikant/fabrikant-descendent/general_study.csv"
file4 = "results/fabrikant/fabrikant-ascendent/general_study.csv"

nomrai_df = pd.read_csv(file1, sep="|", index_col="id")
fixed30_df = pd.read_csv(file2, sep="|", index_col="id")
descendent_df = pd.read_csv(file3, sep="|", index_col="id")
ascendent_df = pd.read_csv(file4, sep="|", index_col="id")

messages_df = pd.DataFrame()

messages_df["no-mrai"] = nomrai_df["total_messages"].values
messages_df["30-fixed"] = fixed30_df["total_messages"].values
messages_df["descendent"] = descendent_df["total_messages"].values
messages_df["ascendent"] = ascendent_df["total_messages"].values

boxplot = messages_df.boxplot()
plt.savefig("results/fabrikant/messages_comparison.pdf", format="pdf")
plt.close()

convergence_time = pd.DataFrame()

convergence_time["no-mrai"] = nomrai_df["convergence_time"].values
convergence_time["30-fixed"] = fixed30_df["convergence_time"].values
convergence_time["descendent"] = descendent_df["convergence_time"].values
convergence_time["ascendent"] = ascendent_df["convergence_time"].values

boxplot = convergence_time.boxplot()
plt.savefig("results/fabrikant/convergence_time.pdf", format="pdf")

plt.close()
