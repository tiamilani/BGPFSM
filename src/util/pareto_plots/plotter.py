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

def plot_scatter(x: np.array, y: np.array, pareto_front=None, label="label", 
                 xlabel="xlabel", ylabel="ylabel", title="title", 
                 output_file_name="out_scatter.pdf", colormap=['b', 'r']):

    fig, ax = plt.subplots()
    ax.scatter(x, y, c=colormap[0], label=label)
    if pareto_front is not None:
        ax.scatter(pareto_front[0], pareto_front[1], c=colormap[1], label="pareto_front")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                     box.width, box.height * 0.9])
    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
              fancybox=True, ncol=2)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.title(title)

    plt.savefig(output_file_name, format="pdf")
    plt.close()

def legends(lns, axes):
    labs = [l.get_label() for l in lns]
    # Shrink current axis's height by 10% on the bottom
    box = axes[0].get_position()
    for ax in axes:
        ax.set_position([box.x0, box.y0 + box.height * 0.15,
                         box.width, box.height * 0.9])
    # Put a legend below current axis
    lgd = axes[0].legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.15),
              fancybox=True, ncol=2)
    return lgd

def plot_line(x, y, color, label="label", ax=None, marker=None):
    l = ax.plot(x, y, color, label=label, marker=marker)
    return l

def get_axes():
    fig, ax = plt.subplots()
    return (fig, ax)

def plot_messages_time_comparison(x, time, messages, title="title", 
                                  output_file_name="mrai_evolution.pdf"):

    fig, ax = plt.subplots()
    ax2 = ax.twinx()

    l1 = plot_line(x, time, 'g', label="Convergence time", ax=ax)
    l2 = plot_line(x, messages, 'r', label="# Messages", ax=ax2)

    lns = l1 + l2
    legends(lns, [ax, ax2])

    ax.set_xlabel("MRAI value")
    ax.set_ylabel("Convergence time [s]")
    ax2.set_ylabel("# Packets")
    ax.set_title(title)

    fig.savefig(output_file_name, format="pdf")
    plt.close()

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def plot_messages_suppression_time_comparison(x, time, messages, suppression, 
                                  title="title", 
                                  output_file_name="mrai_evolution.pdf"):

    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.75)
    ax2 = ax.twinx()
    ax3 = ax.twinx()

    ax3.spines["right"].set_position(("axes", 1.2))
    make_patch_spines_invisible(ax3)
    ax3.spines["right"].set_visible(True)

    l1 = plot_line(x, time, 'g', label="Convergence time", ax=ax)
    l2 = plot_line(x, messages, 'r', label="# Messages", ax=ax2)
    l3 = plot_line(x, suppression, 'b', label="Suppressions", ax=ax3)

    lns = l1 + l2 + l3
    legends(lns, [ax, ax2, ax3])

    ax.set_xlabel("MRAI value")
    ax.set_ylabel("Convergence time [s]")
    ax2.set_ylabel("# Packets")
    ax3.set_ylabel("# Suppressions")
    ax.set_title(title)

    fig.savefig(output_file_name, format="pdf")
    plt.close()


def plot_messages_time_comparison_error_bars(x, time, messages, std_time, std_messages,
        title="Title", output_file_name="mrai_evolution_errorBars.pdf"):

    fig, ax = plt.subplots()
    ax2 = ax.twinx()

    l1 = plot_line(x, time, 'g', label="Convergence time", ax=ax)
    l2 = plot_line(x, messages, 'r', label="# Messages", ax=ax2)

    ax.errorbar(x, time, yerr = std_time, fmt="none", color='g')
    ax2.errorbar(x, messages, yerr = std_messages, fmt="none", color='r')

    lns = l1 + l2
    legends(lns, [ax, ax2])

    ax.set_xlabel("MRAI value")
    ax.set_ylabel("Convergence time [s]")
    ax2.set_ylabel("# Packets")
    ax.set_title(title)

    fig.savefig(output_file_name, format="pdf")
    plt.close()

def plot_messages_time_comparison_error_bars_alpha(x, time, messages, std_time, 
        std_messages, title="Title", output_file_name="mrai_evolution_errorBars.pdf"):

    fig, ax = plt.subplots()
    ax2 = ax.twinx()

    l1 = plot_line(x, time, 'g', label="Convergence time", ax=ax)
    l2 = plot_line(x, messages, 'r', label="# Messages", ax=ax2)

    time_y1 = time - std_time
    time_y2 = time + std_time
    ax.fill_between(x, time_y2, time_y1, facecolor='g', alpha=0.5)
    
    msg_y1 = messages - std_messages
    msg_y2 = messages + std_messages
    ax2.fill_between(x, msg_y2, msg_y1, facecolor='r', alpha=0.5)

    lns = l1 + l2
    legends(lns, [ax, ax2])

    ax.set_xlabel("MRAI value")
    ax.set_ylabel("Convergence time [s]")
    ax2.set_ylabel("# Packets")
    ax.set_title(title)

    fig.savefig(output_file_name, format="pdf")
    plt.close()

def plot_boxplot_pandasDataframe(df, title="Title", ylabel="ylabel", output_file_name="boxplot.pdf"):

    fig, ax = plt.subplots()
    ax.boxplot(df)

    ticks = range(1, len(df.columns)+1)
    labels = list(df.columns)

    ax.set_title(title)
    ax.set_ylabel(ylabel)

    plt.xticks(ticks,labels)
    plt.xticks(rotation=45)
    plt.margins(0.2)
    plt.subplots_adjust(bottom=0.30)

    fig.savefig(output_file_name, format="pdf")
    plt.close()
